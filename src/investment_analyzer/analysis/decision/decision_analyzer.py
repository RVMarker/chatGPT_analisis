"""High-level adapter for the V11 decision engine.

Keeps the decision calculation independent from report-generation code.
"""

from __future__ import annotations

from typing import Any, Mapping

from .decision_engine import DecisionEngine, DecisionResult


class DecisionAnalyzer:
    """Build strategic and tactical investment verdicts."""

    def __init__(self, engine: DecisionEngine | None = None) -> None:
        self.engine = engine or DecisionEngine()

    def build(
        self,
        fundamental_score: float,
        dcf_score: float,
        comparables_score: float,
        macro_score: float,
        risk_score: float,
        technical_score: float,
        sentiment_score: float,
        smart_money_score: float,
        provider_quality: float = 80.0,
        freshness: float = 80.0,
        consistency: float = 80.0,
        completeness: float = 80.0,
        strengths: list[str] | None = None,
        red_flags: list[str] | None = None,
        counter_thesis: list[str] | None = None,
    ) -> dict[str, Any]:
        """Return both horizons plus explicit evidence and counter-thesis."""
        result = self.engine.evaluate(
            strategic_scores={
                "fundamental": fundamental_score,
                "valuation": dcf_score,
                "comparables": comparables_score,
                "macro": macro_score,
                "risk": risk_score,
            },
            tactical_scores={
                "technical": technical_score,
                "sentiment": sentiment_score,
                "smart_money": smart_money_score,
                "macro": macro_score,
            },
            confidence_inputs={
                "provider_quality": provider_quality,
                "freshness": freshness,
                "consistency": consistency,
                "completeness": completeness,
            },
            strengths=strengths or [],
            red_flags=red_flags or [],
        )

        return {
            "result": result,
            "strategic": result,
            "tactical": result,
            "counter_thesis": counter_thesis or [],
        }

    def build_from_context(self, context: Any) -> dict[str, Any]:
        """Build a decision from an AnalysisContext.

        Missing optional fields are treated conservatively as neutral (50),
        while required module outputs remain explicit and easy to diagnose.
        """
        fundamentals = _mapping(context.fundamentals)
        valuation = _mapping(context.valuation)
        comparables = _mapping(context.comparables)
        macro = _mapping(context.macro)
        risk = _mapping(context.risk)
        technical = _mapping(context.technical)
        sentiment = _mapping(context.sentiment)
        asset = context.asset

        return self.build(
            fundamental_score=_score(fundamentals),
            dcf_score=_score(valuation),
            comparables_score=_score(comparables),
            macro_score=_score(macro),
            risk_score=_score(risk),
            technical_score=_score(technical),
            sentiment_score=_score(sentiment),
            smart_money_score=_value(asset, "smart_money_score", 50.0),
            provider_quality=_value(asset, "provider_quality", 80.0),
            freshness=_value(asset, "data_freshness", 80.0),
            consistency=_value(asset, "provider_consistency", 80.0),
            completeness=_value(asset, "completeness", 80.0),
            strengths=_list(risk, "strengths"),
            red_flags=_list(risk, "red_flags"),
            counter_thesis=_list(risk, "counter_thesis"),
        )


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _score(value: Mapping[str, Any]) -> float:
    for key in ("score", "normalized_score", "total_score"):
        if key in value:
            return _number(value[key], 50.0)
    return 50.0


def _value(obj: Any, key: str, default: float) -> float:
    if isinstance(obj, Mapping):
        return _number(obj.get(key), default)
    return _number(getattr(obj, key, default), default)


def _number(value: Any, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(100.0, number))


def _list(value: Mapping[str, Any], key: str) -> list[str]:
    data = value.get(key, [])
    if isinstance(data, list):
        return [str(item) for item in data]
    return []
