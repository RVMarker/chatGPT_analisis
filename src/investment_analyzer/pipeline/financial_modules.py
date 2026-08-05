"""Adapters that execute the real financial engines inside AnalysisPipeline."""
from __future__ import annotations

from dataclasses import asdict

from investment_analyzer.analysis.context.analysis_context import AnalysisContext
from investment_analyzer.analysis.integration.fundamental_valuation_risk import FinancialAnalysisIntegrator


class FinancialModuleAdapter:
    """Runs Fundamental/Valuation/Risk once and exposes their results to the pipeline."""

    def __init__(self, integrator=None):
        self.integrator = integrator or FinancialAnalysisIntegrator()

    def run(self, context: AnalysisContext):
        asset = context.asset
        statements = getattr(asset, "financials", None)
        price = getattr(asset, "price", None)
        if statements is None:
            raise ValueError("Asset no contiene financials normalizados")
        if price is None:
            raise ValueError("Asset no contiene price normalizado")

        integrated = self.integrator.run(statements, price)
        context.fundamentals = integrated.fundamental.as_dict()
        context.risk = integrated.risk.as_dict()
        if integrated.valuation is not None:
            context.valuation = integrated.valuation.as_dict()
            context.dcf = context.valuation.get("dcf") or {}
        else:
            context.valuation = {}
            context.dcf = {}
        return context
