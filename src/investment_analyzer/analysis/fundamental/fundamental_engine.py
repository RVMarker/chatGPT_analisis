"""Fundamental scoring engine V11.

Scores normalized financial statements without downloading data itself.
The engine deliberately separates raw metrics from the decision score so the
same logic can later be replayed against historical snapshots.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class FundamentalResult:
    score: float
    growth_score: float
    profitability_score: float
    balance_sheet_score: float
    cash_flow_score: float
    quality_score: float
    metrics: dict[str, Any]
    red_flags: list[str]
    strengths: list[str]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class FundamentalEngine:
    """Build a 0-100 fundamental score from a FinancialStatements object."""

    @staticmethod
    def _ratio(numerator, denominator):
        if numerator is None or denominator in (None, 0):
            return None
        try:
            return float(numerator) / float(denominator)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _bounded(value: float | None, low: float = 0, high: float = 100) -> float:
        if value is None:
            return 50.0
        return max(low, min(high, float(value)))

    def calculate(self, statements) -> FundamentalResult:
        bs = statements.balance
        inc = statements.income
        cf = statements.cashflow

        current_ratio = self._ratio(bs.current_assets, bs.current_liabilities)
        debt_to_equity = self._ratio(bs.total_liabilities, bs.shareholders_equity)
        net_margin = self._ratio(inc.net_income, inc.revenue)
        operating_margin = self._ratio(inc.operating_income, inc.revenue)
        interest_coverage = self._ratio(inc.ebit, abs(inc.interest_expense))
        fcf_margin = self._ratio(cf.free_cash_flow, inc.revenue)

        growth_score = 50.0
        profitability_score = 50.0
        balance_score = 50.0
        cash_flow_score = 50.0
        quality_score = 50.0
        strengths: list[str] = []
        red_flags: list[str] = []

        if net_margin is not None:
            profitability_score = self._bounded(50 + net_margin * 250)
            if net_margin > 0.10:
                strengths.append("Margen neto positivo y sólido")
            elif net_margin < 0:
                red_flags.append("Margen neto negativo")

        if operating_margin is not None:
            profitability_score = (profitability_score + self._bounded(50 + operating_margin * 200)) / 2

        if current_ratio is not None:
            balance_score = self._bounded(50 + (current_ratio - 1.0) * 35)
            if current_ratio >= 1.5:
                strengths.append("Liquidez corriente saludable")
            elif current_ratio < 1:
                red_flags.append("Pasivos corrientes superiores a activos corrientes")

        if debt_to_equity is not None:
            balance_score = (balance_score + self._bounded(100 - debt_to_equity * 50)) / 2
            if debt_to_equity > 2:
                red_flags.append("Apalancamiento deuda/patrimonio elevado")

        if interest_coverage is not None:
            coverage_score = self._bounded(interest_coverage * 20)
            balance_score = (balance_score + coverage_score) / 2
            if interest_coverage < 1:
                red_flags.append("EBIT insuficiente para cubrir intereses")
            elif interest_coverage >= 5:
                strengths.append("Cobertura de intereses fuerte")

        if cf.free_cash_flow is not None:
            cash_flow_score = self._bounded(50 + (fcf_margin or 0) * 250)
            if cf.free_cash_flow > 0:
                strengths.append("Flujo de caja libre positivo")
            else:
                red_flags.append("Flujo de caja libre negativo")

        if inc.ebit is not None and inc.net_income is not None:
            accrual_gap = abs(float(inc.ebit) - float(inc.net_income))
            quality_score = self._bounded(100 - self._ratio(accrual_gap, abs(inc.ebit) or 1) * 100)

        score = (
            growth_score * 0.15
            + profitability_score * 0.30
            + balance_score * 0.25
            + cash_flow_score * 0.20
            + quality_score * 0.10
        )

        metrics = {
            "current_ratio": current_ratio,
            "debt_to_equity": debt_to_equity,
            "net_margin": net_margin,
            "operating_margin": operating_margin,
            "interest_coverage": interest_coverage,
            "fcf_margin": fcf_margin,
            "fiscal_date": statements.fiscal_date,
        }
        return FundamentalResult(
            score=round(score, 2),
            growth_score=round(growth_score, 2),
            profitability_score=round(profitability_score, 2),
            balance_sheet_score=round(balance_score, 2),
            cash_flow_score=round(cash_flow_score, 2),
            quality_score=round(quality_score, 2),
            metrics=metrics,
            red_flags=red_flags,
            strengths=strengths,
        )
