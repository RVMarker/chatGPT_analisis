"""Fundamental scoring engine V11.

Scores normalized financial statements without downloading data itself.
Missing evidence is represented as N/D and excluded from the weighted score;
it is never silently converted to a neutral 50.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class FundamentalResult:
    score: float | None
    growth_score: float | None
    profitability_score: float | None
    balance_sheet_score: float | None
    cash_flow_score: float | None
    quality_score: float | None
    metrics: dict[str, Any]
    red_flags: list[str]
    strengths: list[str]
    available_components: list[str]
    unavailable_components: list[str]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class FundamentalEngine:
    """Build an auditable 0-100 fundamental score from financial statements."""

    @staticmethod
    def _ratio(numerator, denominator):
        if numerator is None or denominator in (None, 0):
            return None
        try:
            return float(numerator) / float(denominator)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _bounded(value: float | None, low: float = 0, high: float = 100) -> float | None:
        if value is None:
            return None
        return max(low, min(high, float(value)))

    def calculate(self, statements) -> FundamentalResult:
        bs = statements.balance
        inc = statements.income
        cf = statements.cashflow

        current_ratio = self._ratio(bs.current_assets, bs.current_liabilities)
        debt_to_equity = self._ratio(bs.total_liabilities, bs.shareholders_equity)
        net_margin = self._ratio(inc.net_income, inc.revenue)
        operating_margin = self._ratio(inc.operating_income, inc.revenue)
        interest_coverage = self._ratio(inc.ebit, abs(inc.interest_expense) if inc.interest_expense is not None else None)
        fcf_margin = self._ratio(cf.free_cash_flow, inc.revenue)

        profitability_score = None
        balance_score = None
        cash_flow_score = None
        quality_score = None
        growth_score = None
        strengths: list[str] = []
        red_flags: list[str] = []

        if net_margin is not None:
            profitability_score = self._bounded(50 + net_margin * 250)
            if net_margin > 0.10:
                strengths.append("Margen neto positivo y sólido")
            elif net_margin < 0:
                red_flags.append("Margen neto negativo")

        if operating_margin is not None:
            operating_score = self._bounded(50 + operating_margin * 200)
            profitability_score = operating_score if profitability_score is None else (profitability_score + operating_score) / 2

        balance_components: list[float] = []
        if current_ratio is not None:
            balance_components.append(self._bounded(50 + (current_ratio - 1.0) * 35))
            if current_ratio >= 1.5:
                strengths.append("Liquidez corriente saludable")
            elif current_ratio < 1:
                red_flags.append("Pasivos corrientes superiores a activos corrientes")

        if debt_to_equity is not None:
            balance_components.append(self._bounded(100 - debt_to_equity * 50))
            if debt_to_equity > 2:
                red_flags.append("Apalancamiento deuda/patrimonio elevado")

        if interest_coverage is not None:
            balance_components.append(self._bounded(interest_coverage * 20))
            if interest_coverage < 1:
                red_flags.append("EBIT insuficiente para cubrir intereses")
            elif interest_coverage >= 5:
                strengths.append("Cobertura de intereses fuerte")

        if balance_components:
            balance_score = sum(balance_components) / len(balance_components)

        if cf.free_cash_flow is not None and fcf_margin is not None:
            cash_flow_score = self._bounded(50 + fcf_margin * 250)
            if cf.free_cash_flow > 0:
                strengths.append("Flujo de caja libre positivo")
            else:
                red_flags.append("Flujo de caja libre negativo")

        if inc.ebit is not None and inc.net_income is not None:
            accrual_gap = abs(float(inc.ebit) - float(inc.net_income))
            quality_score = self._bounded(100 - self._ratio(accrual_gap, abs(inc.ebit) or 1) * 100)

        unavailable_components = [
            name for name, value in {
                "growth": growth_score,
                "profitability": profitability_score,
                "balance_sheet": balance_score,
                "cash_flow": cash_flow_score,
                "quality": quality_score,
            }.items() if value is None
        ]
        component_values = {
            "growth": (growth_score, 0.15),
            "profitability": (profitability_score, 0.30),
            "balance_sheet": (balance_score, 0.25),
            "cash_flow": (cash_flow_score, 0.20),
            "quality": (quality_score, 0.10),
        }
        available = {
            name: (value, weight)
            for name, (value, weight) in component_values.items()
            if value is not None
        }
        if available:
            total_weight = sum(weight for _, weight in available.values())
            score = round(sum(value * (weight / total_weight) for value, weight in available.values()), 2)
        else:
            score = None
            red_flags.append("Fundamental: ningún componente disponible; score N/D")

        return FundamentalResult(
            score=score,
            growth_score=round(growth_score, 2) if growth_score is not None else None,
            profitability_score=round(profitability_score, 2) if profitability_score is not None else None,
            balance_sheet_score=round(balance_score, 2) if balance_score is not None else None,
            cash_flow_score=round(cash_flow_score, 2) if cash_flow_score is not None else None,
            quality_score=round(quality_score, 2) if quality_score is not None else None,
            metrics={
                "current_ratio": current_ratio,
                "debt_to_equity": debt_to_equity,
                "net_margin": net_margin,
                "operating_margin": operating_margin,
                "interest_coverage": interest_coverage,
                "fcf_margin": fcf_margin,
                "fiscal_date": statements.fiscal_date,
            },
            red_flags=red_flags,
            strengths=strengths,
            available_components=list(available),
            unavailable_components=unavailable_components,
        )
