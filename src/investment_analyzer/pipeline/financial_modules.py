"""Adapters that execute the real financial engines inside AnalysisPipeline."""
from __future__ import annotations

from investment_analyzer.analysis.context.analysis_context import AnalysisContext
from investment_analyzer.analysis.integration.fundamental_valuation_risk import FinancialAnalysisIntegrator


def _as_mapping(value):
    if isinstance(value, dict):
        return value
    if hasattr(value, "as_dict"):
        return value.as_dict()
    raise TypeError(f"Resultado financiero no normalizado: {type(value).__name__}")


class FinancialModuleAdapter:
    """Run Fundamental/Valuation/Risk once from normalized context data."""

    def __init__(self, integrator=None):
        self.integrator = integrator or FinancialAnalysisIntegrator()
        self.fundamental_engine = self.integrator.fundamental
        self.valuation_engine = self.integrator.valuation
        self.risk_engine = self.integrator.risk

    def run(self, context: AnalysisContext):
        if context.financials is None:
            raise ValueError("AnalysisContext no contiene financials normalizados")
        if context.price is None:
            raise ValueError("AnalysisContext no contiene price normalizado")

        integrated = self.integrator.run(context.financials, context.price)

        context.fundamentals = _as_mapping(integrated.fundamental)
        context.risk = _as_mapping(integrated.risk)

        valuation = _as_mapping(integrated.valuation)
        if valuation.get("available", True) and valuation.get("score") is not None:
            context.valuation = valuation
            context.valuation["available"] = True
            context.dcf = context.valuation.get("dcf") or {}
        else:
            context.valuation = {**valuation, "available": False, "score": None}
            context.dcf = {}

        context.metadata.setdefault("financial_integration", {})
        context.metadata["financial_integration"].update(
            {
                "fundamental_available": context.fundamentals.get("score") is not None,
                "valuation_available": context.valuation.get("available", False),
                "risk_available": context.risk.get("score") is not None,
            }
        )
        return context
