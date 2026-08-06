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

    @staticmethod
    def _technical_quality(context):
        result = getattr(context, "technical_result", {}) or {}
        if not isinstance(result, dict):
            return 50.0
        if not result.get("available", False):
            return 40.0
        requirements = result.get("requirements", {}) or {}
        if not requirements:
            return 60.0
        available = sum(bool(v) for v in requirements.values())
        return round(50.0 + 50.0 * available / len(requirements), 2)

    @staticmethod
    def _collect_strengths(context):
        strengths = []
        technical = getattr(context, "technical", {}) or {}
        if isinstance(technical, dict):
            score = DecisionModule._score(technical)
            if score >= 70:
                strengths.append(f"Technical score favorable ({score:.1f}/100)")
        fundamentals = getattr(context, "fundamentals", {}) or {}
        if isinstance(fundamentals, dict) and DecisionModule._score(fundamentals) >= 70:
            strengths.append("Fundamental score favorable")
        return strengths

    @staticmethod
    def _collect_red_flags(context):
        flags = []
        technical = getattr(context, "technical", {}) or {}
        if isinstance(technical, dict):
            flags.extend(str(x) for x in technical.get("warnings", []) or [])
        return flags

    def run(self, context):
        fundamental = self._score(context.fundamentals)
        valuation = self._score(context.valuation)
        risk = self._score(context.risk)
        technical = self._score(context.technical)
        sentiment = self._score(context.sentiment)
        smart_money = self._score(context.metadata.get("smart_money", 50.0))

        provider_data = context.metadata.get("data_providers", {})
        required = [provider_data.get("price"), provider_data.get("financials")]
        completeness = 100.0 if all(required) else 50.0
        provider_quality = 90.0 if all(p == "yahoo" for p in required if p) else 80.0
        technical_quality = self._technical_quality(context)
        freshness = 80.0 if provider_data.get("history") else 60.0

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
                "freshness": freshness,
                "consistency": 80.0,
                "completeness": completeness,
                "technical_data_quality": technical_quality,
            },
            strengths=self._collect_strengths(context),
            red_flags=self._collect_red_flags(context),
            contextual={
                "comparables": self._score(context.comparables),
                "macro": self._score(context.macro),
            },
        )
        context.decision = result
        return result
