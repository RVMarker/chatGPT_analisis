"""High-level adapter for the V12.81 decision engine."""
from __future__ import annotations
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping
from .decision_engine import DecisionEngine

class DecisionAnalyzer:
    def __init__(self, engine: DecisionEngine | None = None) -> None:
        self.engine = engine or DecisionEngine()

    def build(self, fundamental_score: float, dcf_score: float, comparables_score: float, macro_score: float,
              risk_score: float, technical_score: float, sentiment_score: float, smart_money_score: float,
              provider_quality: float = 80.0, freshness: float = 80.0, consistency: float = 80.0,
              completeness: float = 80.0, valuation_quality: float | str | None = None,
              strengths: list[str] | None = None, red_flags: list[str] | None = None,
              counter_thesis: list[str] | None = None, peer_valuation_score: float | None = None,
              interest_rate_score: float | None = None) -> dict[str, Any]:
        result = self.engine.evaluate(
            strategic_scores={"fundamental": fundamental_score, "valuation": dcf_score,
                              "technical": technical_score, "risk": risk_score},
            tactical_scores={"technical": technical_score, "sentiment": sentiment_score,
                             "smart_money": smart_money_score},
            confidence_inputs={"provider_quality": provider_quality, "freshness": freshness,
                               "consistency": consistency, "completeness": completeness,
                               "valuation_quality": valuation_quality},
            strengths=strengths or [], red_flags=red_flags or [],
            contextual={"comparables": comparables_score, "peer_valuation": peer_valuation_score,
                        "macro": macro_score, "interest_rate_context": interest_rate_score},
        )
        return {"result": result,
                "strategic": {"decision": result.strategic_decision, "score": result.strategic_score, "breakdown": result.strategic_breakdown},
                "tactical": {"decision": result.tactical_decision, "score": result.tactical_score, "breakdown": result.tactical_breakdown},
                "confidence": result.confidence, "contextual": result.contextual,
                "counter_thesis": counter_thesis or [], "strengths": result.strengths, "red_flags": result.red_flags}

    def build_from_context(self, context: Any) -> dict[str, Any]:
        fundamentals, valuation, dcf = _mapping(context.fundamentals), _mapping(context.valuation), _mapping(context.dcf)
        comparables, macro, risk = _mapping(context.comparables), _mapping(context.macro), _mapping(context.risk)
        technical, sentiment, asset = _mapping(context.technical), _mapping(context.sentiment), context.asset
        valuation_source = dcf if _has_score(dcf) else valuation
        peer_score = _score(comparables) if _has_score(comparables) else None
        interest_score = _value(macro, "interest_rate_score", None)
        return self.build(_score(fundamentals), _score(valuation_source), _score(comparables), _score(macro), _score(risk),
                          _score(technical), _score(sentiment), _value(asset, "smart_money_score", 50.0),
                          _value(asset, "provider_quality", 80.0), _value(asset, "data_freshness", 80.0),
                          _value(asset, "provider_consistency", 80.0), _value(asset, "completeness", 80.0),
                          valuation_source.get("valuation_quality"), _merge_lists(fundamentals, risk, key="strengths"),
                          _merge_lists(fundamentals, risk, key="red_flags"), _list(risk, "counter_thesis"), peer_score, interest_score)

def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping): return value
    if is_dataclass(value): return asdict(value)
    return {}

def _has_score(value): return any(key in value and value[key] is not None for key in ("score", "normalized_score", "total_score"))
def _score(value):
    for key in ("score", "normalized_score", "total_score"):
        if key in value: return _number(value[key], 50.0)
    return 50.0

def _value(obj, key, default):
    value=obj.get(key) if isinstance(obj, Mapping) else getattr(obj, key, default)
    return _number(value, default) if value is not None else default

def _number(value, default):
    try: number = float(value)
    except (TypeError, ValueError): return default
    return max(0.0, min(100.0, number)) if number is not None else default

def _list(value, key):
    data = value.get(key, [])
    return [str(item) for item in data] if isinstance(data, list) else []

def _merge_lists(*values, key):
    result = []
    for value in values:
        for item in _list(value, key):
            if item not in result: result.append(item)
    return result
