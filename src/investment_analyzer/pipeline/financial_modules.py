"""Adapters that execute the real financial engines inside AnalysisPipeline."""
from __future__ import annotations

from investment_analyzer.analysis.context.analysis_context import AnalysisContext
from investment_analyzer.analysis.integration.fundamental_valuation_risk import FinancialAnalysisIntegrator


class FinancialModuleAdapter:
    """Run Fundamental/Valuation/Risk once from normalized context data."""

    def __init__(self, integrator=None):
        self.integrator = integrator or FinancialAnalysisIntegrator()

    def run(self, context: AnalysisContext):
        if context.financials is None:
            raise ValueError("AnalysisContext no contiene financials normalizados")
        if context.price is None:
            raise ValueError("AnalysisContext no contiene price normalizado")

        integrated = self.integrator.run(context.financials, context.price)

        # Fundamental and Risk are real normalized scores; never replace them
        # with a neutral 50 merely because valuation is unavailable.
        context.fundamentals = integrated.fundamental.as_dict()
        context.risk = integrated.risk.as_dict()

        if integrated.valuation is not None:
            context.valuation = integrated.valuation.as_dict()
            context.valuation["available"] = True
            context.dcf = context.valuation.get("dcf") or {}
        else:
            # DCF unavailable is explicitly represented as unavailable.
            # Decision code must not interpret this as a 50/100 valuation score.
            context.valuation = {
                "available": False,
                "score": None,
                "reason": "DCF no disponible: faltan supuestos explícitos o datos suficientes",
            }
            context.dcf = {}

        return context
