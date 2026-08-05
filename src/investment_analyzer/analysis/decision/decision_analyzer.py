"""High-level adapter for the V11 decision engine.

Keeps decision calculation independent from report-generation code and accepts
both dictionaries and V11 dataclass results produced by analysis engines.
"""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .decision_engine import DecisionEngine


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
        result = self.engine.evaluate(
            strategic_scores={
                "fundamental": fundamental_score,
                "valuation": dcf_score,
                # Contextual only: intentionally ignored by DecisionEngine.
                "comparables": comparables_score,
                "macro": macro_score,
                "risk": risk_score,
            },
            tactical_scores={
                "technical": technical_score,
                "sentiment": sentiment_score,
                "smart_money": smart_money_score,
                # Contextual only: intentionally ignored by DecisionEngine.
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
            contextual={
                "comparables": comparables_score,
                "macro": macro_score,
            },
        )

        return {
            "result": result,
            "strategic": {
                "decision": result.strategic_decision,
                "score": result.strategic_score,
                "breakdown": result.strategic_breakdown,
            },
            "tactical": {
                "decision": result.tactical_decision,
                "score": result.tactical_score,
                "breakdown": result.tactical_breakdown,
            },
            "confidence": result.confidence,
            "contextual": result.contextual,
            "counter_thesis": counter_thesis or [],
            "strengths": result.strengths,
            "red_flags": result.red_flags,
        }

    def build_from_context(self, context: Any) -> dict[str, Any]:
        fundamentals = _mapping(context.fundamentals)
        valuation = _mapping(context.valuation)
        dcf = _mapping(context.dcf)
        comparables = _mapping(context.comparables)
        macro = _mapping(context.macro)
        risk = _mapping(context.risk)
        technical = _mapping(context.technical)
        sentiment = _mapping(context.sentiment)
        asset = context.asset

        # Prefer the explicit DCF result if valuation and DCF are both present.
        valuation_source = dcf if _has_score(dcf) else valuation
        return self.build(
            fundamental_score=_score(fundamentals),
            dcf_score=_score(valuation_source),
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
            strengths=_merge_lists(fundamentals, risk, "strengths"),
            red_flags=_merge_lists(fundamentals, risk, "red_flags"),
            counter_thesis=_list(risk, "counter_thesis"),
        )


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    if is_dataclass(value):
        return asdict(value)
    return {}


def _has_score(value: Mapping[str, Any]) -> bool:
    return any(key in value and value[key] is not None for key in ("score", "normalized_score", "total_score"))


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
    return [str(item) for item in data] if isinstance(data, list) else []


def _merge_lists(*values: Mapping[str, Any], key: str) -> list[str]:
    result: list[str] = []
    for value in values:
        for item in _list(value, key):
            if item not in result:
                result.append(item)
    return result
