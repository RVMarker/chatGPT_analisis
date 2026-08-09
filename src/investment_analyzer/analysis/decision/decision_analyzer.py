"""High-level adapter for the V12 decision engine."""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .decision_engine import DecisionEngine


class DecisionAnalyzer:
    def __init__(self, engine: DecisionEngine | None = None) -> None:
        self.engine = engine or DecisionEngine()

    def build(
        self,
        fundamental_score: float | None,
        dcf_score: float | None,
        comparables_score: float | None,
        macro_score: float | None,
        risk_score: float | None,
        technical_score: float | None,
        sentiment_score: float | None,
        smart_money_score: float | None,
        provider_quality: float | None = None,
        freshness: float | None = None,
        consistency: float | None = None,
        completeness: float | None = None,
        valuation_quality: float | str | None = None,
        strengths: list[str] | None = None,
        red_flags: list[str] | None = None,
        counter_thesis: list[str] | None = None,
    ) -> dict[str, Any]:
        result = self.engine.evaluate(
            strategic_scores={
                "fundamental": fundamental_score,
                "valuation": dcf_score,
                "technical": technical_score,
                "risk": risk_score,
            },
            tactical_scores={
                "technical": technical_score,
                "sentiment": sentiment_score,
                "smart_money": smart_money_score,
            },
            confidence_inputs={
                "provider_quality": provider_quality,
                "freshness": freshness,
                "consistency": consistency,
                "completeness": completeness,
                "valuation_quality": valuation_quality,
            },
            strengths=strengths or [],
            red_flags=red_flags or [],
            contextual={"comparables": comparables_score, "macro": macro_score},
        )
        return {
            "result": result,
            "strategic": {"decision": result.strategic_decision, "score": result.strategic_score, "breakdown": result.strategic_breakdown},
            "tactical": {"decision": result.tactical_decision, "score": result.tactical_score, "breakdown": result.tactical_breakdown},
            "confidence": result.confidence,
            "contextual": result.contextual,
            "counter_thesis": counter_thesis or [],
            "strengths": result.strengths,
            "red_flags": result.red_flags,
        }

    def build_from_context(self, context: Any) -> dict[str, Any]:
        fundamentals, valuation, dcf = _mapping(context.fundamentals), _mapping(context.valuation), _mapping(context.dcf)
        comparables, macro, risk = _mapping(context.comparables), _mapping(context.macro), _mapping(context.risk)
        technical, sentiment, asset = _mapping(context.technical), _mapping(context.sentiment), context.asset
        valuation_source = dcf if _has_score(dcf) else valuation
        return self.build(
            _score(fundamentals),
            _score(valuation_source),
            _score(comparables),
            _score(macro),
            _score(risk),
            _score(technical),
            _score(sentiment),
            _value(asset, "smart_money_score"),
            _value(asset, "provider_quality"),
            _value(asset, "data_freshness"),
            _value(asset, "provider_consistency"),
            _value(asset, "completeness"),
            valuation_source.get("valuation_quality"),
            _merge_lists(fundamentals, risk, key="strengths"),
            _merge_lists(fundamentals, risk, key="red_flags"),
            _list(risk, "counter_thesis"),
        )


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    if is_dataclass(value):
        return asdict(value)
    return {}


def _has_score(value):
    return any(key in value and value[key] is not None for key in ("score", "normalized_score", "total_score"))


def _score(value):
    for key in ("score", "normalized_score", "total_score"):
        if key in value:
            return _number(value[key], None)
    return None


def _value(obj, key, default=None):
    value = obj.get(key) if isinstance(obj, Mapping) else getattr(obj, key, default)
    return _number(value, default)


def _number(value, default=None):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(100.0, number))


def _list(value, key):
    data = value.get(key, [])
    return [str(item) for item in data] if isinstance(data, list) else []


def _merge_lists(*values, key):
    result = []
    for value in values:
        for item in _list(value, key):
            if item not in result:
                result.append(item)
    return result
