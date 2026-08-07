"""Integration boundary for the V11 fundamental/valuation/risk engines."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from investment_analyzer.analysis.fundamental.fundamental_engine import FundamentalEngine
from investment_analyzer.analysis.risk.risk_engine import RiskEngine
from investment_analyzer.analysis.valuation.dcf_engine import DCFEngine, DCFResult
from investment_analyzer.analysis.valuation.reit_engine import REITValuationEngine
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
    """Run Fundamental/Risk and the appropriate valuation model."""

    def __init__(self, fundamental=None, valuation=None, risk=None, reit_valuation=None):
        self.fundamental = fundamental or FundamentalEngine()
        self.valuation = valuation or DCFEngine()
        self.risk = risk or RiskEngine()
        self.reit_valuation = reit_valuation or REITValuationEngine()

    def run(
        self,
        statements: FinancialStatements,
        price: PriceData,
        *,
        growth_rates: list[float] | None = None,
        wacc: float | None = None,
        terminal_growth: float | None = None,
        net_debt: float | None = None,
        asset_type: str | None = None,
        reit_required_yield: float = 0.09,
        reit_growth: float = 0.03,
    ) -> IntegratedFinancialAnalysis:
        if price.current <= 0:
            raise ValueError("El precio actual debe ser positivo")

        fundamental = self.fundamental.calculate(statements)
        balance = statements.balance
        income = statements.income
        cashflow = statements.cashflow
        debt = net_debt
        if debt is None:
            debt = float(balance.long_term_debt or 0) - float(balance.cash or 0)

        risk = self.risk.calculate(statements, market_value_equity=price.market_cap)
        valuation: dict[str, Any]
        valuation_warnings: list[str] = []
        is_reit = str(asset_type or "").upper() in {"REIT", "FIBRA"}

        if is_reit and price.shares_outstanding:
            # Prefer official FFO/AFFO when the provider supplies it. Only fall
            # back to the explicitly labelled proxy; never infer AFFO from FCF.
            ffo = cashflow.ffo_official if cashflow.ffo_official is not None else cashflow.ffo_proxy
            source_quality = "FFO_OFFICIAL" if cashflow.ffo_official is not None else "FFO_PROXY"
            if ffo is not None:
                reit = self.reit_valuation.calculate(
                    ffo=float(ffo),
                    shares_outstanding=float(price.shares_outstanding),
                    current_price=float(price.current),
                    required_yield=reit_required_yield,
                    growth=reit_growth,
                    source_quality=source_quality,
                    affo=cashflow.affo_official,
                    distribution=cashflow.dividends_paid,
                    property_value=balance.property_value,
                    net_debt=debt,
                    ebitda=income.ebitda,
                    interest_expense=income.interest_expense,
                )
                valuation = reit.as_dict()
                valuation["model"] = "FFO_CAPITALIZATION"
                valuation["ffo_proxy"] = cashflow.ffo_proxy
                valuation["ffo_official"] = cashflow.ffo_official
                valuation["affo_official"] = cashflow.affo_official
                valuation["assumptions"] = {"required_yield": reit_required_yield, "growth": reit_growth}
                valuation_warnings.extend(reit.warnings)
            else:
                valuation = {"available": False, "score": None, "model": "FFO_CAPITALIZATION",
                              "warnings": ["FIBRA/REIT detectado pero no existe FFO disponible"]}
        elif growth_rates and wacc is not None and terminal_growth is not None:
            fcf = cashflow.free_cash_flow
            if fcf is not None:
                dcf: DCFResult = self.valuation.calculate(
                    fcf_base=float(fcf), growth_rates=growth_rates,
                    wacc=float(wacc), terminal_growth=float(terminal_growth),
                    net_debt=debt, shares_outstanding=price.shares_outstanding,
                    current_price=price.current,
                )
                valuation = dcf.as_dict()
                valuation["available"] = dcf.fair_value_per_share is not None
                valuation["score"] = REITValuationEngine._score(dcf.margin_of_safety) if dcf.margin_of_safety is not None else None
                valuation_warnings.extend(dcf.warnings)
            else:
                valuation = {"available": False, "score": None, "warnings": ["Falta free_cash_flow para ejecutar el DCF"]}
        else:
            valuation = {
                "available": False, "score": None,
                "warnings": [
                    "Valuation no ejecutada: faltan datos/modelo específico para el activo",
                    "No se utiliza un supuesto artificial para producir una valoración",
                ],
            }

        strengths = list(dict.fromkeys(fundamental.strengths + risk.strengths))
        red_flags = list(dict.fromkeys(fundamental.red_flags + risk.red_flags + valuation_warnings + valuation.get("warnings", [])))
        return IntegratedFinancialAnalysis(
            fundamental=fundamental.as_dict(), valuation=valuation,
            risk=risk.as_dict(), strengths=strengths, red_flags=red_flags,
        )
