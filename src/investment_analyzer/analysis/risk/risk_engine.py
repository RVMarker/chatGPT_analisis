"""V11 risk aggregation layer.

Combines solvency and balance-sheet diagnostics into a normalized 0-100 risk
quality score. Higher score means better risk quality. Raw diagnostics remain
visible for auditability.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from .altman import AltmanCalculator


@dataclass(slots=True)
class RiskResult:
    score: float
    altman_score: float | None
    altman_classification: str
    debt_to_equity: float | None
    current_ratio: float | None
    interest_coverage: float | None
    red_flags: list[str]
    strengths: list[str]
    metrics: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class RiskEngine:
    """Produce an auditable risk score from normalized financial statements."""

    @staticmethod
    def _ratio(a, b):
        if a is None or b in (None, 0):
            return None
        try:
            return float(a) / float(b)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _bounded(value):
        if value is None:
            return 50.0
        return max(0.0, min(100.0, float(value)))

    def calculate(self, statements, market_value_equity: float | None = None) -> RiskResult:
        bs = statements.balance
        inc = statements.income
        red_flags: list[str] = []
        strengths: list[str] = []

        debt_equity = self._ratio(bs.total_liabilities, bs.shareholders_equity)
        current_ratio = self._ratio(bs.current_assets, bs.current_liabilities)
        interest_coverage = self._ratio(inc.ebit, abs(inc.interest_expense))

        balance_score = 50.0
        if debt_equity is not None:
            balance_score = self._bounded(100 - debt_equity * 40)
            if debt_equity > 2:
                red_flags.append("Deuda/patrimonio elevada")
            elif debt_equity < 0.75:
                strengths.append("Apalancamiento moderado")

        liquidity_score = 50.0
        if current_ratio is not None:
            liquidity_score = self._bounded(50 + (current_ratio - 1) * 35)
            if current_ratio < 1:
                red_flags.append("Liquidez corriente inferior a 1")
            elif current_ratio >= 1.5:
                strengths.append("Liquidez corriente saludable")

        coverage_score = 50.0
        if interest_coverage is not None:
            coverage_score = self._bounded(interest_coverage * 15)
            if interest_coverage < 1:
                red_flags.append("Cobertura de intereses inferior a 1x")
            elif interest_coverage >= 5:
                strengths.append("Cobertura de intereses fuerte")

        altman_score = None
        altman_classification = "Datos insuficientes"
        try:
            if market_value_equity is not None:
                working_capital = bs.working_capital
                if working_capital is None and bs.current_assets is not None and bs.current_liabilities is not None:
                    working_capital = bs.current_assets - bs.current_liabilities
                altman = AltmanCalculator.calculate(
                    working_capital,
                    bs.retained_earnings,
                    inc.ebit,
                    market_value_equity,
                    bs.total_liabilities,
                    inc.revenue,
                    bs.total_assets,
                )
                if altman.complete:
                    altman_score = altman.score
                altman_classification = altman.classification
                if altman.classification == "Alto Riesgo":
                    red_flags.append("Altman Z en zona de alto riesgo")
                elif altman.classification == "Excelente":
                    strengths.append("Altman Z en zona financiera fuerte")
        except (ValueError, TypeError, AttributeError):
            pass

        altman_component = 50.0 if altman_score is None else self._bounded(altman_score)
        score = (
            balance_score * 0.30
            + liquidity_score * 0.20
            + coverage_score * 0.20
            + altman_component * 0.30
        )

        return RiskResult(
            score=round(score, 2),
            altman_score=altman_score,
            altman_classification=altman_classification,
            debt_to_equity=debt_equity,
            current_ratio=current_ratio,
            interest_coverage=interest_coverage,
            red_flags=red_flags,
            strengths=strengths,
            metrics={"debt_to_equity": debt_equity, "current_ratio": current_ratio, "interest_coverage": interest_coverage},
        )
