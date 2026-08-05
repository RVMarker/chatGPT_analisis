"""Integration boundary for the real V11 fundamental/valuation/risk engines.

This module intentionally performs no network I/O. Provider adapters are
responsible for producing normalized FinancialStatements and PriceData.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from investment_analyzer.analysis.fundamental import FundamentalEngine
from investment_analyzer.analysis.risk.risk_engine import RiskEngine
from investment_analyzer.analysis.valuation import DCFEngine, DCFResult
from investment_analyzer.common.models import FinancialStatements, PriceData


@dataclass(slots=True)
class IntegratedFinancialAnalysis:
    fundamental: dict[str, Any]
    valuation: dict[str, Any]
    risk: dict[str, Any]
    strengths: list[str]
    red_flags: list[str]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class FinancialAnalysisIntegrator:
    """Run the three strategic engines against one normalized snapshot."""

    def __init__(self, fundamental=None, valuation=None, risk=None):
        self.fundamental = fundamental or FundamentalEngine()
        self.valuation = valuation or DCFEngine()
        self.risk = risk or RiskEngine()

    def run(
        self,
        statements: FinancialStatements,
        price: PriceData,
        *,
        growth_rates: list[float],
        wacc: float,
        terminal_growth: float,
        net_debt: float | None = None,
    ) -> IntegratedFinancialAnalysis:
        if price.current <= 0:
            raise ValueError("El precio actual debe ser positivo")
        if not growth_rates:
            raise ValueError("Se requiere al menos una tasa de crecimiento para el DCF")

        fundamental = self.fundamental.calculate(statements)
        balance = statements.balance
        debt = net_debt
        if debt is None:
            debt = float(balance.long_term_debt or 0) - float(balance.cash or 0)

        fcf = statements.cashflow.free_cash_flow
        if fcf is None:
            raise ValueError("Falta free_cash_flow para ejecutar el DCF")

        dcf: DCFResult = self.valuation.calculate(
            fcf_base=float(fcf),
            growth_rates=growth_rates,
            wacc=wacc,
            terminal_growth=terminal_growth,
            net_debt=debt,
            shares_outstanding=price.shares_outstanding,
            current_price=price.current,
        )
        risk = self.risk.calculate(
            statements,
            market_value_equity=price.market_cap,
        )

        strengths = list(dict.fromkeys(fundamental.strengths + risk.strengths))
        red_flags = list(dict.fromkeys(fundamental.red_flags + risk.red_flags + dcf.warnings))
        return IntegratedFinancialAnalysis(
            fundamental=fundamental.as_dict(),
            valuation=dcf.as_dict(),
            risk=risk.as_dict(),
            strengths=strengths,
            red_flags=red_flags,
        )
