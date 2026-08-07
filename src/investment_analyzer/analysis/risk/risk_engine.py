"""V11 risk aggregation layer.

Combines solvency and balance-sheet diagnostics into a normalized 0-100 risk
quality score. Higher score means better risk quality. Raw diagnostics remain
visible for auditability. Missing components do not become a neutral 50.

For REIT/FIBRA-like capital structures, market leverage can corroborate book
leverage when current-assets/current-liabilities or EBIT/interest coverage are
not supplied by a provider. Debt/EBITDA is also used when EBITDA is available,
because it measures debt burden relative to operating capacity rather than
repeating the debt/equity ratio.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from .altman import AltmanCalculator


@dataclass(slots=True)
class RiskResult:
    score: float | None
    altman_score: float | None
    altman_classification: str
    debt_to_equity: float | None
    debt_to_ebitda: float | None
    current_ratio: float | None
    interest_coverage: float | None
    market_leverage: float | None
    red_flags: list[str]
    strengths: list[str]
    metrics: dict[str, Any]
    available_components: list[str]
    unavailable_components: list[str]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class RiskEngine:
    """Produce an auditable risk score from normalized financial statements."""

    MIN_CORROBORATING_COMPONENTS = 2

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
            return None
        return max(0.0, min(100.0, float(value)))

    @staticmethod
    def _market_leverage_score(net_debt: float | None, market_value_equity: float | None):
        """Convert net debt / market equity into a transparent 0-100 quality score."""
        leverage = RiskEngine._ratio(net_debt, market_value_equity)
        if leverage is None:
            return None, None
        score = RiskEngine._bounded(100.0 - leverage * 50.0)
        return leverage, score

    @staticmethod
    def _debt_ebitda_score(debt_to_ebitda: float | None):
        """Map debt/EBITDA to a conservative quality score.

        <=1x is treated as strong (100); >=6x as weak (0). The interpolation
        is a transparent model convention, not an industry threshold claim.
        """
        if debt_to_ebitda is None:
            return None
        return RiskEngine._bounded(100.0 - ((debt_to_ebitda - 1.0) * 20.0))

    def calculate(self, statements, market_value_equity: float | None = None) -> RiskResult:
        bs = statements.balance
        inc = statements.income
        red_flags: list[str] = []
        strengths: list[str] = []

        debt_equity = self._ratio(bs.total_liabilities, bs.shareholders_equity)
        debt_to_ebitda = self._ratio(bs.long_term_debt, inc.ebitda)
        current_ratio = self._ratio(bs.current_assets, bs.current_liabilities)
        interest_coverage = self._ratio(
            inc.ebit,
            abs(inc.interest_expense) if inc.interest_expense is not None else None,
        )

        balance_score = self._bounded(100 - debt_equity * 40) if debt_equity is not None else None
        debt_ebitda_score = self._debt_ebitda_score(debt_to_ebitda)
        liquidity_score = self._bounded(50 + (current_ratio - 1) * 35) if current_ratio is not None else None
        coverage_score = self._bounded(interest_coverage * 15) if interest_coverage is not None else None

        net_debt = None
        if bs.long_term_debt is not None:
            net_debt = float(bs.long_term_debt) - float(bs.cash or 0)
        market_leverage, market_leverage_score = self._market_leverage_score(net_debt, market_value_equity)

        if debt_equity is not None:
            if debt_equity > 2:
                red_flags.append("Deuda/patrimonio elevada")
            elif debt_equity < 0.75:
                strengths.append("Apalancamiento moderado")
        if debt_to_ebitda is not None:
            if debt_to_ebitda > 6:
                red_flags.append("Deuda/EBITDA elevada")
            elif debt_to_ebitda <= 2:
                strengths.append("Deuda/EBITDA contenida")
        if current_ratio is not None:
            if current_ratio < 1:
                red_flags.append("Liquidez corriente inferior a 1")
            elif current_ratio >= 1.5:
                strengths.append("Liquidez corriente saludable")
        if interest_coverage is not None:
            if interest_coverage < 1:
                red_flags.append("Cobertura de intereses inferior a 1x")
            elif interest_coverage >= 5:
                strengths.append("Cobertura de intereses fuerte")
        if market_leverage is not None:
            if market_leverage > 0.50:
                red_flags.append("Apalancamiento de mercado elevado")
            elif market_leverage < 0.35:
                strengths.append("Apalancamiento de mercado moderado")

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

        components = {
            "balance": (balance_score, 0.20),
            "debt_ebitda": (debt_ebitda_score, 0.20),
            "liquidity": (liquidity_score, 0.15),
            "coverage": (coverage_score, 0.15),
            "altman": (self._bounded(altman_score), 0.20),
            "market_leverage": (market_leverage_score, 0.10),
        }
        available = {name: (score, weight) for name, (score, weight) in components.items() if score is not None}
        unavailable = [name for name, (score, _) in components.items() if score is None]

        if len(available) < self.MIN_CORROBORATING_COMPONENTS:
            score = None
            red_flags.append(
                f"Riesgo: corroboración insuficiente ({len(available)}/{len(components)} componentes); score N/D"
            )
        else:
            total_weight = sum(weight for _, weight in available.values())
            score = sum(score_value * (weight / total_weight) for score_value, weight in available.values())
            score = round(score, 2)

        return RiskResult(
            score=score,
            altman_score=altman_score,
            altman_classification=altman_classification,
            debt_to_equity=debt_equity,
            debt_to_ebitda=debt_to_ebitda,
            current_ratio=current_ratio,
            interest_coverage=interest_coverage,
            market_leverage=market_leverage,
            red_flags=red_flags,
            strengths=strengths,
            metrics={
                "debt_to_equity": debt_equity,
                "debt_to_ebitda": debt_to_ebitda,
                "current_ratio": current_ratio,
                "interest_coverage": interest_coverage,
                "market_leverage": market_leverage,
            },
            available_components=list(available),
            unavailable_components=unavailable,
        )
