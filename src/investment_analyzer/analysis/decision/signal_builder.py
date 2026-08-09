"""V12.90: build decision-engine inputs from actual pipeline data.

Missing evidence stays missing; this module never substitutes a neutral 50.
"""
from __future__ import annotations
from collections.abc import Mapping
from typing import Any


def _lookup(source: Any, keys: tuple[str, ...]):
    if isinstance(source, Mapping):
        for key in keys:
            value = source.get(key)
            if value is not None:
                return value
        for value in source.values():
            found = _lookup(value, keys)
            if found is not None:
                return found
    elif isinstance(source, (list, tuple)):
        for value in source:
            found = _lookup(value, keys)
            if found is not None:
                return found
    return None


def _score(source: Any, keys: tuple[str, ...]):
    value = _lookup(source, keys)
    if isinstance(value, Mapping):
        value = value.get("score")
    try:
        return max(0.0, min(100.0, float(value))) if value is not None else None
    except (TypeError, ValueError):
        return None


def build_decision_inputs(*, enriched: Mapping[str, Any], specialized: Mapping[str, Any], analysis: Mapping[str, Any] | None = None):
    sources = (analysis or {}, specialized, enriched)
    def first(keys):
        for source in sources:
            value = _score(source, keys)
            if value is not None:
                return value
        return None

    strategic = {
        "fundamental": first(("fundamental_score", "fundamental", "fundamental_analysis_score")),
        "valuation": first(("valuation_score", "dcf_score", "intrinsic_value_score", "valuation")),
        "technical": first(("technical_score", "technical", "technical_analysis_score")),
        "risk": first(("risk_score", "risk", "risk_adjusted_score")),
    }
    tactical = {
        "technical": strategic["technical"],
        "sentiment": first(("sentiment_score", "sentiment", "market_sentiment_score")),
        "smart_money": first(("smart_money_score", "smart_money", "smart_money_flow_score")),
    }
    contextual = {
        "comparables": first(("comparables_score", "comparables", "peer_score")),
        "peer_valuation": first(("peer_valuation_score", "pe_valuation_vs_peers", "ev_ebitda_vs_peers")),
        "macro": first(("macro_score", "macro", "macro_context_score")),
        "interest_rate_context": first(("interest_rate_context", "interest_rate_score", "rates_score")),
    }
    confidence_inputs = {
        "provider_quality": first(("provider_quality", "data_quality")) or 0.0,
        "freshness": first(("freshness", "freshness_score")) or 0.0,
        "consistency": first(("consistency", "consistency_score")) or 0.0,
        "completeness": first(("completeness", "completeness_score")) or 0.0,
        "technical_data_quality": first(("technical_data_quality", "technical_quality")) or 0.0,
        "valuation_quality": _lookup({**dict(enriched), **dict(specialized)}, ("valuation_quality",)),
    }
    return strategic, tactical, contextual, confidence_inputs
