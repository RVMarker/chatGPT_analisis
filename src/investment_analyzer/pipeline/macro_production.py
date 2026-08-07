"""Production macroeconomic context for V11."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
BANXICO_BASE = "https://www.banxico.org.mx/SieAPIRest/service/v1/series"

if load_dotenv is not None:
    load_dotenv()


@dataclass(slots=True)
class MacroSnapshot:
    series_id: str
    value: float | None
    date: str | None
    provider: str
    title: str


class ProductionMacroModule:
    """Fetch and summarize macro context without voting in the decision."""

    FRED_SERIES = {
        "policy_rate": ("FEDFUNDS", "Fed funds rate"),
        "inflation_yoy": ("CPIAUCSL", "US CPI"),
        "unemployment": ("UNRATE", "US unemployment"),
        "real_gdp_yoy": ("GDPC1", "US real GDP"),
        "treasury_10y": ("DGS10", "US 10Y Treasury"),
    }

    MEXICO_FRED_SERIES = {
        "treasury_10y": ("IRLTLT01MXM156N", "Mexico 10Y government bond yield (OECD/FRED)"),
    }

    BANXICO_SERIES = {
        "policy_rate": ("SF61745", "Banxico target rate"),
        "inflation_yoy": ("SP30578", "Mexico annual inflation"),
        "usd_mxn": ("SF43718", "USD/MXN FIX"),
    }

    def __init__(self, timeout: float = 12.0, session: requests.Session | None = None):
        self.timeout = timeout
        self.session = session or requests.Session()

    @staticmethod
    def _is_mexico(symbol: str) -> bool:
        return (symbol or "").upper().endswith(".MX")

    @staticmethod
    def _latest(observations: list[dict[str, Any]]) -> tuple[float | None, str | None]:
        for item in reversed(observations or []):
            raw = item.get("value") if "value" in item else item.get("dato")
            if raw in (None, "", ".", "N/D"):
                continue
            try:
                return float(str(raw).replace(",", "")), item.get("date") or item.get("fecha")
            except (TypeError, ValueError):
                continue
        return None, None

    @staticmethod
    def _fred_api_key() -> str | None:
        return os.getenv("FRED_API_KEY") or os.getenv("FRED_KEY")

    @staticmethod
    def _banxico_token() -> str | None:
        return (
            os.getenv("BANXICO_TOKEN")
            or os.getenv("BANXICO_KEY")
            or os.getenv("BMX_TOKEN")
            or os.getenv("BANXICO_API_KEY")
        )

    @staticmethod
    def _response_diagnostic(response: Any) -> str | None:
        try:
            text = str(getattr(response, "text", "") or "").strip()
        except Exception:  # pragma: no cover - defensive
            return None
        if not text:
            return None
        text = re.sub(r"\b[A-Za-z0-9]{32,}\b", "[REDACTED]", text)
        text = " ".join(text.split())
        return text[:240]

    def _fred(self, series_id: str, title: str, units: str = "lin") -> MacroSnapshot:
        api_key = self._fred_api_key()
        if not api_key:
            return MacroSnapshot(series_id, None, None, "fred", title)
        response = self.session.get(
            FRED_BASE,
            params={
                "series_id": series_id,
                "api_key": api_key,
                "file_type": "json",
                "sort_order": "asc",
                "limit": 100,
                "units": units,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        value, date = self._latest(response.json().get("observations", []))
        return MacroSnapshot(series_id, value, date, "fred", title)

    def _banxico_batch(self) -> dict[str, MacroSnapshot]:
        token = self._banxico_token()
        result = {
            series_id: MacroSnapshot(series_id, None, None, "banxico", title)
            for _, (series_id, title) in self.BANXICO_SERIES.items()
        }
        if not token:
            return result

        series_ids = ",".join(series_id for series_id, _ in self.BANXICO_SERIES.values())
        response = self.session.get(
            f"{BANXICO_BASE}/{series_ids}/datos/oportuno",
            headers={
                "Bmx-Token": token,
                "Accept": "application/json",
                "User-Agent": "investment-analyzer-v11",
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        series = response.json().get("bmx", {}).get("series", [])
        expected_ids = [series_id for series_id, _ in self.BANXICO_SERIES.values()]
        for index, item in enumerate(series):
            # Production responses identify each series with idSerie. Some test
            # doubles and legacy gateways omit it; in that case the API contract
            # still preserves the requested order, so map by position.
            series_id = item.get("idSerie")
            if not series_id and index < len(expected_ids):
                series_id = expected_ids[index]
            if series_id not in result:
                continue
            value, date = self._latest(item.get("datos", []))
            current = result[series_id]
            result[series_id] = MacroSnapshot(series_id, value, date, current.provider, current.title)
        return result

    @staticmethod
    def _regime(policy: float | None, inflation: float | None, growth: float | None, unemployment: float | None) -> str:
        if policy is None and inflation is None:
            return "SIN DATOS"
        pressure = 0
        if policy is not None and policy >= 8:
            pressure += 2
        elif policy is not None and policy >= 5:
            pressure += 1
        if inflation is not None and inflation >= 5:
            pressure += 2
        elif inflation is not None and inflation >= 3.5:
            pressure += 1
        if growth is not None and growth < 0:
            pressure += 2
        if unemployment is not None and unemployment >= 6:
            pressure += 1
        return "RESTRICTIVO" if pressure >= 3 else "NEUTRAL" if pressure >= 1 else "FAVORABLE"

    @staticmethod
    def _required_margin(us: dict[str, Any], mx: dict[str, Any] | None) -> float:
        rates = [us.get("policy_rate")]
        if mx:
            rates.append(mx.get("policy_rate"))
        valid = [float(x) for x in rates if isinstance(x, (int, float))]
        if not valid:
            return 15.0
        highest = max(valid)
        if highest >= 9:
            return 35.0
        if highest >= 7:
            return 30.0
        if highest >= 5:
            return 25.0
        return 15.0

    @staticmethod
    def _cross_country_context(us: dict[str, Any], mx: dict[str, Any] | None) -> dict[str, float | None]:
        """Compute Mexico-vs-US macro spreads for context only; never a decision vote."""
        if not mx:
            return {
                "policy_rate_spread_mx_us": None,
                "treasury_10y_spread_mx_us": None,
                "mexico_real_rate_ex_post": None,
            }

        def spread(mx_key: str, us_key: str) -> float | None:
            mx_value, us_value = mx.get(mx_key), us.get(us_key)
            if isinstance(mx_value, (int, float)) and isinstance(us_value, (int, float)):
                return round(float(mx_value) - float(us_value), 2)
            return None

        real_rate = None
        if isinstance(mx.get("policy_rate"), (int, float)) and isinstance(mx.get("inflation_yoy"), (int, float)):
            real_rate = round(float(mx["policy_rate"]) - float(mx["inflation_yoy"]), 2)

        return {
            "policy_rate_spread_mx_us": spread("policy_rate", "policy_rate"),
            "treasury_10y_spread_mx_us": spread("treasury_10y", "treasury_10y"),
            "mexico_real_rate_ex_post": real_rate,
        }

    def run(self, context) -> dict[str, Any]:
        symbol = getattr(getattr(context, "asset", None), "symbol", "")
        fred_configured = self._fred_api_key() is not None
        banxico_configured = self._banxico_token() is not None
        us: dict[str, Any] = {}
        errors: list[str] = []

        for key, (series_id, title) in self.FRED_SERIES.items():
            units = "pc1" if key in {"inflation_yoy", "real_gdp_yoy"} else "lin"
            try:
                snap = self._fred(series_id, title, units=units)
            except requests.HTTPError as exc:
                status = getattr(getattr(exc, "response", None), "status_code", None)
                suffix = f" HTTP {status}" if status else ""
                snap = MacroSnapshot(series_id, None, None, "fred", title)
                errors.append(f"FRED {series_id}: HTTPError{suffix}")
            except Exception as exc:
                snap = MacroSnapshot(series_id, None, None, "fred", title)
                errors.append(f"FRED {series_id}: {type(exc).__name__}")
            us[key] = snap.value
            us[f"{key}_date"] = snap.date

        mx: dict[str, Any] | None = None
        if self._is_mexico(symbol):
            mx = {key: None for key in self.BANXICO_SERIES}
            for key in self.BANXICO_SERIES:
                mx[f"{key}_date"] = None

            for key, (series_id, title) in self.MEXICO_FRED_SERIES.items():
                try:
                    snap = self._fred(series_id, title, units="lin")
                except requests.HTTPError as exc:
                    status = getattr(getattr(exc, "response", None), "status_code", None)
                    suffix = f" HTTP {status}" if status else ""
                    snap = MacroSnapshot(series_id, None, None, "fred", title)
                    errors.append(f"FRED {series_id}: HTTPError{suffix}")
                except Exception as exc:
                    snap = MacroSnapshot(series_id, None, None, "fred", title)
                    errors.append(f"FRED {series_id}: {type(exc).__name__}")
                mx[key] = snap.value
                mx[f"{key}_date"] = snap.date
                mx[f"{key}_provider"] = snap.provider if snap.value is not None else None
                mx[f"{key}_series"] = series_id

            try:
                snapshots = self._banxico_batch()
                for key, (series_id, _) in self.BANXICO_SERIES.items():
                    snap = snapshots[series_id]
                    mx[key] = snap.value
                    mx[f"{key}_date"] = snap.date
            except requests.HTTPError as exc:
                response = getattr(exc, "response", None)
                status = getattr(response, "status_code", None)
                suffix = f" HTTP {status}" if status else ""
                diagnostic = self._response_diagnostic(response)
                detail = f" — {diagnostic}" if diagnostic else ""
                errors.append(f"Banxico batch: HTTPError{suffix}{detail}")
            except Exception as exc:
                errors.append(f"Banxico batch: {type(exc).__name__}")

        us_regime = self._regime(
            us.get("policy_rate"), us.get("inflation_yoy"),
            us.get("real_gdp_yoy"), us.get("unemployment"),
        )
        mx_regime = None
        if mx is not None:
            mx_regime = self._regime(mx.get("policy_rate"), mx.get("inflation_yoy"), None, None)

        fred_observations = sum(
            value is not None for key, value in us.items()
            if not key.endswith("_date") and key != "errors"
        )
        mexico_observation_keys = set(self.BANXICO_SERIES) | set(self.MEXICO_FRED_SERIES)
        mexico_observations = 0
        if mx is not None:
            # Count only actual macro measurements, never traceability metadata
            # such as *_provider or *_series.
            mexico_observations = sum(mx.get(key) is not None for key in mexico_observation_keys)

        diagnostics = {
            "fred_configured": fred_configured,
            "banxico_configured": banxico_configured if mx is not None else None,
            "fred_observations": fred_observations,
            "mexico_observations": mexico_observations,
            "errors": errors,
        }
        cross_country = self._cross_country_context(us, mx)

        return {
            "available": bool(fred_observations or mexico_observations),
            "context_only": True,
            "score": None,
            "required_margin": self._required_margin(us, mx),
            "provider": "fred+banxico" if mx is not None else "fred",
            "us": us,
            "mexico": mx,
            "cross_country": cross_country,
            "us_regime": us_regime,
            "mexico_regime": mx_regime,
            "diagnostics": diagnostics,
            "explanation": "Macro es contexto; no vota directamente en BUY/SELL/HOLD.",
        }
