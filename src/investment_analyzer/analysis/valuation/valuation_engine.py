"""Unified valuation layer for V11."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from .dcf_engine import DCFEngine, DCFResult


@dataclass(slots=True)
class ValuationResult:
    score: float | None
    dcf: DCFResult | None
    upside: float | None
    margin_of_safety: float | None
    warnings: list[str]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class ValuationEngine:
    """Turns DCF output into the normalized valuation score used by V11."""

    @staticmethod
    def _score_from_upside(upside: float | None) -> float | None:
        if upside is None:
            return None
        return max(0.0, min(100.0, 50.0 + float(upside) * (50.0 / 0.30)))

    def from_dcf(
        self,
        fcf_base: float,
        growth_rates: list[float],
        wacc: float,
        terminal_growth: float,
        *,
        net_debt: float = 0.0,
        shares_outstanding: float | None = None,
        current_price: float | None = None,
    ) -> ValuationResult:
        dcf = DCFEngine().calculate(
            fcf_base,
            growth_rates,
            wacc,
            terminal_growth,
            net_debt,
            shares_outstanding,
            current_price,
        )
        warnings = list(dcf.warnings)
        score = self._score_from_upside(dcf.margin_of_safety)
        if score is None:
            warnings.append("Valuation score no disponible: no existe margen de seguridad calculable")
        return ValuationResult(
            score=round(score, 2) if score is not None else None,
            dcf=dcf,
            upside=dcf.margin_of_safety,
            margin_of_safety=dcf.margin_of_safety,
            warnings=warnings,
        )
