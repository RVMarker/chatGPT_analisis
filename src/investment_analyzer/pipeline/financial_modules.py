"""Adapters that execute the real financial engines inside AnalysisPipeline."""
from __future__ import annotations

from investment_analyzer.analysis.context.analysis_context import AnalysisContext
from investment_analyzer.analysis.integration.fundamental_valuation_risk import FinancialAnalysisIntegrator
from investment_analyzer.analysis.valuation.reit_engine import REITValuationEngine
from investment_analyzer.analysis.data_quality.reit_gate import REITDataQualityGate


def _as_mapping(value):
    if isinstance(value, dict):
        return value
    if hasattr(value, "as_dict"):
        return value.as_dict()
    raise TypeError(f"Resultado financiero no normalizado: {type(value).__name__}")


def _reit_gate_input(context: AnalysisContext) -> dict:
    """Build only evidence-backed fields; missing values remain None."""
    f = context.financials
    b = getattr(f, "balance", None)
    i = getattr(f, "income", None)
    c = getattr(f, "cashflow", None)
    p = context.price
    return {
        "ffo": getattr(c, "ffo_official", None) or getattr(c, "ffo_proxy", None),
        "affo": getattr(c, "affo_official", None),
        "distribution": getattr(c, "dividends_paid", None),
        "net_debt": ((getattr(b, "long_term_debt", None) or 0) - (getattr(b, "cash", None) or 0)) if getattr(b, "long_term_debt", None) is not None else None,
        "ebitda": getattr(i, "ebitda", None),
        "interest_expense": getattr(i, "interest_expense", None),
        "property_value": getattr(b, "property_value", None),
        "shares_outstanding": getattr(p, "shares_outstanding", None),
        "debt_equity": context.metadata.get("debt_equity"),
    }


class FinancialModuleAdapter:
    """Run Fundamental/Valuation/Risk once from normalized context data."""

    def __init__(self, integrator=None, reit_gate=None):
        self.integrator = integrator or FinancialAnalysisIntegrator()
        self.reit_gate = reit_gate or REITDataQualityGate()
        self.fundamental_engine = self.integrator.fundamental
        self.valuation_engine = self.integrator.valuation
        self.risk_engine = self.integrator.risk

    def run(self, context: AnalysisContext):
        if context.financials is None:
            raise ValueError("AnalysisContext no contiene financials normalizados")
        if context.price is None:
            raise ValueError("AnalysisContext no contiene price normalizado")

        asset_type = getattr(context.asset, "asset_type", None)
        is_reit = str(asset_type or "").upper() in {"FIBRA", "REIT"}

        # V11.9: provenance gate runs before the financial engines. It does not
        # manufacture or backfill missing metrics; it records exactly which
        # evidence is allowed to participate and which fields reduce confidence.
        if is_reit:
            gate_input = _reit_gate_input(context)
            cashflow = context.financials.cashflow
            verified_fields = set()
            if getattr(cashflow, "ffo_official", None) is not None:
                verified_fields.add("ffo")
            if getattr(cashflow, "affo_official", None) is not None:
                verified_fields.add("affo")
            if getattr(cashflow, "distribution_source", None) == "reit_distribution":
                verified_fields.add("distribution")
            gate = self.reit_gate.validate(
                gate_input,
                asset_type="FIBRA" if str(asset_type).upper() == "FIBRA" else "REIT",
                source=context.metadata.get("financial_provider") or "normalized_financials",
                fiscal_date=getattr(context.financials, "fiscal_date", None),
                verified_fields=verified_fields,
            )
            context.metadata["reit_data_quality"] = gate.as_dict()

        integrated = self.integrator.run(
            context.financials,
            context.price,
            asset_type=asset_type,
        )

        context.fundamentals = _as_mapping(integrated.fundamental)
        context.risk = _as_mapping(integrated.risk)

        valuation = _as_mapping(integrated.valuation)
        if valuation.get("available", True) and valuation.get("score") is not None:
            # Keep the decision score mathematically tied to the exact fair value
            # and price exposed in the report. This prevents a stale/mismatched
            # score from one intermediate engine from voting against the numbers
            # actually shown to the user.
            if valuation.get("model") == "FFO_CAPITALIZATION":
                fair_value = valuation.get("fair_value_per_share")
                current_price = getattr(context.price, "current", None)
                if isinstance(fair_value, (int, float)) and isinstance(current_price, (int, float)) and current_price > 0:
                    margin = float(fair_value) / float(current_price) - 1.0
                    valuation["margin_of_safety"] = margin
                    valuation["score"] = REITValuationEngine._score(margin)
                    valuation["decision_price"] = float(current_price)
            context.valuation = valuation
            context.valuation["available"] = True
            context.dcf = context.valuation.get("dcf") or {}
        else:
            context.valuation = {**valuation, "available": False, "score": None}
            context.dcf = {}

        if is_reit:
            gate_data = context.metadata.get("reit_data_quality", {})
            context.valuation["data_quality_gate"] = gate_data
            context.risk["data_quality_gate"] = gate_data
            context.valuation["missing_evidence"] = gate_data.get("missing", [])
            context.risk["blocked_from_vote"] = gate_data.get("blocked_from_vote", [])

        context.metadata.setdefault("financial_integration", {})
        context.metadata["financial_integration"].update(
            {
                "asset_type": asset_type,
                "valuation_model": context.valuation.get("model"),
                "valuation_source_quality": context.valuation.get("source_quality"),
                "fundamental_available": context.fundamentals.get("score") is not None,
                "valuation_available": context.valuation.get("available", False),
                "risk_available": context.risk.get("score") is not None,
                "reit_data_quality_gate": context.metadata.get("reit_data_quality", {}).get("quality") if is_reit else None,
            }
        )
        return context
