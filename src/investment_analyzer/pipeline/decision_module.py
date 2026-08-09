"""Pipeline adapter for the transparent V12 DecisionEngine."""
from __future__ import annotations

from investment_analyzer.analysis.decision.decision_engine import DecisionEngine
from investment_analyzer.pipeline.provider_quality import score_provider_quality


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
            return None
        if not available or not requirements:
            return None
        satisfied = sum(bool(v) for v in requirements.values())
        return round(100.0 * satisfied / len(requirements), 2)

    @staticmethod
    def _collect_strengths(context):
        strengths = []
        technical_score = DecisionModule._score(getattr(context, "technical", {}))
        if technical_score is not None and technical_score >= 70:
            strengths.append(f"Technical score favorable ({technical_score:.1f}/100)")
        fundamental_score = DecisionModule._score(getattr(context, "fundamentals", {}))
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

    @staticmethod
    def _data_quality_inputs(context):
        provider_data = context.metadata.get("data_providers", {}) or {}
        available_groups = [k for k in ("price", "financials", "history") if provider_data.get(k)]
        completeness = round(100.0 * len(available_groups) / 3, 2)
        freshness = None
        raw_freshness = provider_data.get("freshness")
        if raw_freshness is not None:
            try:
                freshness = max(0.0, min(100.0, float(raw_freshness)))
            except (TypeError, ValueError):
                freshness = None
        consistency = None
        raw_consistency = provider_data.get("consistency")
        if raw_consistency is not None:
            try:
                consistency = max(0.0, min(100.0, float(raw_consistency)))
            except (TypeError, ValueError):
                consistency = None
        return {
            "provider_quality": score_provider_quality(provider_data),
            "freshness": freshness,
            "consistency": consistency,
            "completeness": completeness,
            "technical_data_quality": DecisionModule._technical_quality(context),
        }

    def run(self, context):
        fundamental = self._score(context.fundamentals)
        valuation = self._score(context.valuation)
        risk = self._score(context.risk)
        technical = self._score(context.technical)
        sentiment = self._score(context.sentiment)
        smart_money = self._score(context.metadata.get("smart_money"))

        result = self.engine.evaluate(
            strategic_scores={
                "fundamental": fundamental,
                "valuation": valuation,
                "technical": technical,
                "risk": risk,
            },
            tactical_scores={
                "technical": technical,
                "sentiment": sentiment,
                "smart_money": smart_money,
            },
            confidence_inputs=self._data_quality_inputs(context),
            strengths=self._collect_strengths(context),
            red_flags=self._collect_red_flags(context),
            contextual={
                "comparables": self._score(context.comparables),
                "macro": self._score(context.macro),
            },
        )
        context.decision = result
        return result
