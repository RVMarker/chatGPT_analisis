"""Adapters that execute the real financial engines inside AnalysisPipeline."""
from __future__ import annotations

from investment_analyzer.analysis.context.analysis_context import AnalysisContext
from investment_analyzer.analysis.fundamental.fundamental_engine import FundamentalEngine
from investment_analyzer.analysis.integration.fundamental_valuation_risk import FinancialAnalysisIntegrator


class FinancialModuleAdapter:
    """Runs Fundamental/DCF/Risk once and exposes their results to the pipeline."""

    def __init__(self, fundamental=None, integrator=None):
        self.fundamental_engine = fundamental or FundamentalEngine()
        self.integrator = integrator or FinancialAnalysisIntegrator()

    def run(self, context: AnalysisContext):
        asset = context.asset
        statements = getattr(asset, "financials", None)
        price = getattr(asset, "price", None)
        if statements is None:
            raise ValueError("Asset no contiene financials normalizados")
        if price is None:
            raise ValueError("Asset no contiene price normalizado")

        integrated = self.integrator.calculate(statements, price)
        context.fundamentals = integrated.fundamental.as_dict()
        context.valuation = integrated.valuation.as_dict() if integrated.valuation else {}
        context.risk = integrated.risk.as_dict()
        context.metadata["financial_integration"] = integrated.as_dict()
        return context.fundamentals
