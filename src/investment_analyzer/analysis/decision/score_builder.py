"""V12.91 deterministic 0-100 score extraction from analysis outputs.

No defaults are invented: missing metrics remain unavailable.
"""
from __future__ import annotations
from typing import Any, Mapping


def _num(value):
    try:
        if value is None: return None
        return max(0.0, min(100.0, float(value)))
    except (TypeError, ValueError):
        return None


def _first(data: Mapping[str, Any], keys):
    for key in keys:
        if key in data:
            value=data[key]
            if isinstance(value, Mapping):
                if value.get("available") is False: continue
                for k in ("score","normalized_score","total_score","rating"):
                    if k in value: value=value[k]; break
            score=_num(value)
            if score is not None: return score
    return None


def build_scores(context) -> dict[str, Any]:
    f=getattr(context,"fundamentals",{}) or {}
    v=getattr(context,"valuation",{}) or {}
    t=getattr(context,"technical",{}) or {}
    r=getattr(context,"risk",{}) or {}
    s=getattr(context,"sentiment",{}) or {}
    m=(getattr(context,"metadata",{}) or {}).get("smart_money",{}) or {}
    return {
        "strategic": {
            "fundamental": _first(f,("fundamental_score","score","normalized_score","total_score","rating")),
            "valuation": _first(v,("valuation_score","dcf_score","score","normalized_score","total_score","rating")),
            "technical": _first(t,("technical_score","score","normalized_score","total_score","rating")),
            "risk": _first(r,("risk_score","score","normalized_score","total_score","rating")),
        },
        "tactical": {
            "technical": _first(t,("technical_score","score","normalized_score","total_score","rating")),
            "sentiment": _first(s,("sentiment_score","score","normalized_score","total_score","rating")),
            "smart_money": _first(m,("smart_money_score","score","normalized_score","total_score","rating")),
        },
        "contextual": {
            "comparables": _first(getattr(context,"comparables",{}) or {},("comparables_score","peer_valuation_score","score","normalized_score")),
            "macro": _first(getattr(context,"macro",{}) or {},("macro_score","interest_rate_score","score","normalized_score")),
        },
    }
