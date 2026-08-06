"""Pipeline adapter for the transparent V11 DecisionEngine."""
from __future__ import annotations

from investment_analyzer.analysis.decision.decision_engine import DecisionEngine


class DecisionModule:
    """Build the two-horizon verdict from the shared AnalysisContext."""

    def __init__(self, engine: DecisionEngine | None = None):
        self.engine = engine or DecisionEngine()

    @staticmethod
    def _score(value, default=None):
        if isinstance(value, dict):
            if value.get("available") is False:
                return None
            for key in ("score", "total_score", "normalized_score", "rating"):
                if key in value:
                    value = value[key]
                    break
        if value is None:
            return default
        try:
            return max(0.0, min(100.0, float(value)))
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _technical_quality(context):
        result = getattr(context, "technical_result", {}) or {}
        if hasattr(result, "metadata"):
            metadata = result.metadata or {}
            available = bool(metadata.get("available", True))
            requirements = metadata.get("requirements", {}) or {}
        elif isinstance(result, dict):
            available = bool(result.get("available", False))
            requirements = result.get("requirements", {}) or {}
        else:
            return 0.0
        if not available:
            return 0.0
        if not requirements:
            return 50.0
        satisfied = sum(bool(v) for v in requirements.values())
        return round(100.0 * satisfied / len(requirements), 2)

    @staticmethod
    def _collect_strengths(context):
        strengths = []
        technical = getattr(context, "technical", {}) or {}
        technical_score = DecisionModule._score(technical)
        if technical_score is not None and technical_score >= 70:
            strengths.append(f"Technical score favorable ({technical_score:.1f}/100)")
        fundamentals = getattr(context, "fundamentals", {}) or {}
        fundamental_score = DecisionModule._score(fundamentals)
        if fundamental_score is not None and fundamental_score >= 70:
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
        smart_money = self._score(context.metadata.get("smart_money"))

        provider_data = context.metadata.get("data_providers", {})
        provider_values = [provider_data.get("price"), provider_data.get("financials")]
        required_present = sum(bool(value) for value in provider_values)
        completeness = round(100.0 * required_present / len(provider_values), 2) if provider_values else 0.0
        present_providers = [value for value in provider_values if value]
        provider_quality = (
            round(100.0 * sum(value == "yahoo" for value in present_providers) / len(present_providers), 2)
            if present_providers else 0.0
        )
        technical_quality = self._technical_quality(context)
        freshness = 100.0 if provider_data.get("history") else 0.0

        result = self.engine.evaluate(
            strategic_scores={"fundamental": fundamental, "valuation": valuation, "risk": risk},
            tactical_scores={"technical": technical, "sentiment": sentiment, "smart_money": smart_money},
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
