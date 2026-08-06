"""Integration boundary for the V11 fundamental/valuation/risk engines."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from investment_analyzer.analysis.fundamental.fundamental_engine import FundamentalEngine
from investment_analyzer.analysis.risk.risk_engine import RiskEngine
from investment_analyzer.analysis.valuation.dcf_engine import DCFEngine, DCFResult
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
    """Run Fundamental/Risk and DCF only when explicit DCF assumptions exist."""

    def __init__(self, fundamental=None, valuation=None, risk=None):
        self.fundamental = fundamental or FundamentalEngine()
        self.valuation = valuation or DCFEngine()
        self.risk = risk or RiskEngine()

    def run(
        self,
        statements: FinancialStatements,
        price: PriceData,
        *,
        growth_rates: list[float] | None = None,
        wacc: float | None = None,
        terminal_growth: float | None = None,
        net_debt: float | None = None,
    ) -> IntegratedFinancialAnalysis:
        if price.current <= 0:
            raise ValueError("El precio actual debe ser positivo")

        fundamental = self.fundamental.calculate(statements)
        balance = statements.balance
        debt = net_debt
        if debt is None:
            debt = float(balance.long_term_debt or 0) - float(balance.cash or 0)

        risk = self.risk.calculate(
            statements,
            market_value_equity=price.market_cap,
        )

        valuation: dict[str, Any]
        valuation_warnings: list[str] = []
        if growth_rates and wacc is not None and terminal_growth is not None:
            fcf = statements.cashflow.free_cash_flow
            if fcf is not None:
                dcf: DCFResult = self.valuation.calculate(
                    fcf_base=float(fcf),
                    growth_rates=growth_rates,
                    wacc=float(wacc),
                    terminal_growth=float(terminal_growth),
                    net_debt=debt,
                    shares_outstanding=price.shares_outstanding,
                    current_price=price.current,
                )
                valuation = dcf.as_dict()
                valuation_warnings.extend(dcf.warnings)
            else:
                valuation = {"available": False, "score": None, "warnings": ["Falta free_cash_flow para ejecutar el DCF"]}
        else:
            valuation = {
                "available": False,
                "score": None,
                "warnings": [
                    "DCF no ejecutado: faltan growth_rates, WACC y/o terminal_growth explícitos",
                    "No se utiliza un supuesto artificial para producir una valoración",
                ],
            }

        strengths = list(dict.fromkeys(fundamental.strengths + risk.strengths))
        red_flags = list(dict.fromkeys(fundamental.red_flags + risk.red_flags + valuation_warnings + valuation.get("warnings", [])))
        return IntegratedFinancialAnalysis(
            fundamental=fundamental.as_dict(),
            valuation=valuation,
            risk=risk.as_dict(),
            strengths=strengths,
            red_flags=red_flags,
        )
