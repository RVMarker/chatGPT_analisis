"""REIT/FIBRA valuation engine V11.

Uses a transparent FFO-per-share capitalization model. When only public
financial statements are available, the engine can use an explicitly labelled
FFO proxy (net income + depreciation/amortization); it never calls that proxy AFFO.
The assumptions are returned with the result for auditability.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class REITValuationResult:
    available: bool
    method: str
    ffo_per_share: float | None
    fair_value_per_share: float | None
    margin_of_safety: float | None
    score: float | None
    required_yield: float
    growth: float
    source_quality: str
    warnings: list[str]
    valuation_quality: str = "MEDIUM"

    def as_dict(self):
        return asdict(self)


class REITValuationEngine:
    """Dividend/FFO capitalization model appropriate for REIT/FIBRA equity."""

    @staticmethod
    def _rate(name: str, value: float) -> float:
        value = float(value)
        if not 0.0 <= value < 1.0:
            raise ValueError(f"{name} debe estar entre 0 y 1")
        return value

    @staticmethod
    def _score(margin: float | None) -> float | None:
        if margin is None:
            return None
        if margin >= 0.30:
            return 100.0
        if margin >= 0.20:
            return 90.0
        if margin >= 0.10:
            return 80.0
        if margin >= 0.00:
            return 70.0
        if margin >= -0.10:
            return 55.0
        if margin >= -0.20:
            return 40.0
        if margin >= -0.30:
            return 25.0
        return 10.0

    @staticmethod
    def _quality(source_quality: str) -> str:
        quality = (source_quality or "").upper()
        if quality in {"FFO_OFFICIAL", "AFFO_OFFICIAL", "AFFO"}:
            return "HIGH"
        if quality in {"FFO_PROXY", "FFO_ESTIMATE"}:
            return "MEDIUM"
        return "LOW"

    def calculate(
        self,
        *,
        ffo: float,
        shares_outstanding: float,
        current_price: float,
        required_yield: float = 0.09,
        growth: float = 0.03,
        source_quality: str = "FFO_PROXY",
    ) -> REITValuationResult:
        required_yield = self._rate("required_yield", required_yield)
        growth = self._rate("growth", growth)
        valuation_quality = self._quality(source_quality)
        if required_yield <= growth:
            raise ValueError("required_yield debe ser mayor que growth")
        if ffo <= 0:
            return REITValuationResult(
                False, "FFO_CAPITALIZATION", None, None, None, None,
                required_yield, growth, source_quality,
                ["FFO no positivo; no se puede capitalizar de forma robusta"],
                valuation_quality,
            )
        if shares_outstanding <= 0 or current_price <= 0:
            return REITValuationResult(
                False, "FFO_CAPITALIZATION", None, None, None, None,
                required_yield, growth, source_quality,
                ["Faltan acciones en circulación o precio actual válido"],
                valuation_quality,
            )

        ffo_per_share = float(ffo) / float(shares_outstanding)
        fair_value = ffo_per_share * (1.0 + growth) / (required_yield - growth)
        margin = fair_value / float(current_price) - 1.0
        warnings = []
        if source_quality == "FFO_PROXY":
            warnings.append(
                "FFO PROXY: derivado de estados financieros; no sustituye AFFO oficial de la FIBRA"
            )
        if valuation_quality != "HIGH":
            warnings.append(
                f"Calidad de valoración {valuation_quality}: el valor razonable depende de la calidad del FFO disponible"
            )
        if required_yield - growth < 0.04:
            warnings.append("Valoración sensible: spread entre yield requerido y crecimiento < 4pp")
        if margin < 0:
            warnings.append("Precio de mercado supera el valor razonable del modelo FFO")

        return REITValuationResult(
            True, "FFO_CAPITALIZATION", ffo_per_share, fair_value, margin,
            self._score(margin), required_yield, growth, source_quality, warnings,
            valuation_quality,
        )
