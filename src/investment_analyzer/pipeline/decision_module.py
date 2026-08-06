"""Pipeline adapter for the transparent V11 DecisionEngine."""
from __future__ import annotations

from investment_analyzer.analysis.decision.decision_engine import DecisionEngine


class DecisionModule:
    """Build the two-horizon verdict from the shared AnalysisContext.

    Comparables and macro are deliberately passed only as contextual evidence;
    they never enter the weighted strategic/tactical scores.
    """

    def __init__(self, engine: DecisionEngine | None = None):
        self.engine = engine or DecisionEngine()

    @staticmethod
    def _score(value, default=50.0):
        if isinstance(value, dict):
            for key in ("score", "total_score", "normalized_score", "rating"):
                if key in value:
                    value = value[key]
                    break
        try:
            return max(0.0, min(100.0, float(value)))
        except (TypeError, ValueError):
            return default

    def run(self, context):
        fundamental = self._score(context.fundamentals)
        valuation = self._score(context.valuation)
        risk = self._score(context.risk)
        technical = self._score(context.technical)
        sentiment = self._score(context.sentiment)
        smart_money = self._score(context.metadata.get("smart_money", 50.0))

        provider_data = context.metadata.get("data_providers", {})
        available = [provider_data.get("price"), provider_data.get("financials")]
        completeness = 100.0 if all(available) else 50.0
        provider_quality = 90.0 if all(p == "yahoo" for p in available if p) else 80.0

        result = self.engine.evaluate(
            strategic_scores={
                "fundamental": fundamental,
                "valuation": valuation,
                "risk": risk,
            },
            tactical_scores={
                "technical": technical,
                "sentiment": sentiment,
                "smart_money": smart_money,
            },
            confidence_inputs={
                "provider_quality": provider_quality,
                "freshness": 80.0,
                "consistency": 80.0,
                "completeness": completeness,
            },
            contextual={
                "comparables": self._score(context.comparables),
                "macro": self._score(context.macro),
            },
        )
        context.decision = result
        return result
