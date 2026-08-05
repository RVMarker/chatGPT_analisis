"""Unified valuation layer for V11."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from .dcf_engine import DCFEngine, DCFResult


@dataclass(slots=True)
class ValuationResult:
    score: float
    dcf: DCFResult | None
    upside: float | None
    margin_of_safety: float | None
    warnings: list[str]

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data


class ValuationEngine:
    """Turns DCF output into the normalized valuation score used by V11."""

    @staticmethod
    def _score_from_upside(upside: float | None) -> float:
        if upside is None:
            return 50.0
        # +30% upside or more = 100; -30% or worse = 0.
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
        return ValuationResult(
            score=round(self._score_from_upside(dcf.margin_of_safety), 2),
            dcf=dcf,
            upside=dcf.margin_of_safety,
            margin_of_safety=dcf.margin_of_safety,
            warnings=list(dcf.warnings),
        )
