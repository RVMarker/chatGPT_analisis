"""Production macroeconomic context for V11.

Macro is contextual only: it never contributes directly to BUY/SELL/HOLD
scores. US data comes from FRED; Mexican data is added automatically for
Mexican assets (.MX) using Banco de Mexico SIE.

Credentials are read from environment variables. A local ``.env`` file is
loaded automatically when ``python-dotenv`` is installed (it is part of the
recommended ``[full]`` installation):
    FRED_API_KEY
    BANXICO_TOKEN

``BMX_TOKEN`` is accepted as a backwards-compatible alias for Banxico.
Real credentials must never be committed to the repository.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - only relevant for minimal installs
    load_dotenv = None

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
BANXICO_BASE = "https://www.banxico.org.mx/SieAPIRest/service/v1/series"

if load_dotenv is not None:
    # Safe: .env is explicitly ignored by git. Existing process environment
    # variables win because override=False is the default.
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
    # These are current SIE series already used by the project. Keep them
    # centralized so the mapping is auditable and easy to replace if Banxico
    # changes a series identifier.
    BANXICO_SERIES = {
        "policy_rate": ("SF61745", "Banxico target rate"),
        "inflation_yoy": ("SP30578", "Mexico annual inflation"),
        "usd_mxn": ("SF43718", "USD/MXN FIX"),
        "treasury_10y": ("SF63528", "Mexico 10Y government yield"),
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
        return os.getenv("BANXICO_TOKEN") or os.getenv("BMX_TOKEN") or os.getenv("BANXICO_API_KEY")

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

    def _banxico(self, series_id: str, title: str) -> MacroSnapshot:
        token = self._banxico_token()
        if not token:
            return MacroSnapshot(series_id, None, None, "banxico", title)
        response = self.session.get(
            f"{BANXICO_BASE}/{series_id}/datos/oportuno",
            headers={"Bmx-Token": token},
            timeout=self.timeout,
        )
        response.raise_for_status()
        series = response.json().get("bmx", {}).get("series", [])
        datos = series[0].get("datos", []) if series else []
        value, date = self._latest(datos)
        return MacroSnapshot(series_id, value, date, "banxico", title)

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

    def run(self, context) -> dict[str, Any]:
        symbol = getattr(getattr(context, "asset", None), "symbol", "")
        us: dict[str, Any] = {}
        for key, (series_id, title) in self.FRED_SERIES.items():
            units = "pc1" if key in {"inflation_yoy", "real_gdp_yoy"} else "lin"
            try:
                snap = self._fred(series_id, title, units=units)
            except Exception as exc:
                snap = MacroSnapshot(series_id, None, None, "fred", title)
                us.setdefault("errors", []).append(f"{series_id}: {type(exc).__name__}")
            us[key] = snap.value
            us[f"{key}_date"] = snap.date

        mx: dict[str, Any] | None = None
        if self._is_mexico(symbol):
            mx = {}
            for key, (series_id, title) in self.BANXICO_SERIES.items():
                try:
                    snap = self._banxico(series_id, title)
                except Exception as exc:
                    snap = MacroSnapshot(series_id, None, None, "banxico", title)
                    mx.setdefault("errors", []).append(f"{series_id}: {type(exc).__name__}")
                mx[key] = snap.value
                mx[f"{key}_date"] = snap.date

        us_regime = self._regime(us.get("policy_rate"), us.get("inflation_yoy"), us.get("real_gdp_yoy"), us.get("unemployment"))
        mx_regime = None
        if mx is not None:
            mx_regime = self._regime(mx.get("policy_rate"), mx.get("inflation_yoy"), None, None)

        return {
            "available": bool(us.get("policy_rate") is not None or (mx and mx.get("policy_rate") is not None)),
            "context_only": True,
            "score": None,
            "required_margin": self._required_margin(us, mx),
            "provider": "fred+banxico" if mx is not None else "fred",
            "us": us,
            "mexico": mx,
            "us_regime": us_regime,
            "mexico_regime": mx_regime,
            "explanation": "Macro es contexto; no vota directamente en BUY/SELL/HOLD.",
        }
