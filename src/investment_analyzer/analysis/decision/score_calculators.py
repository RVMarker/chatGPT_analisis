"""V12.92 deterministic component scoring from raw analysis metrics."""
from __future__ import annotations
from typing import Any, Mapping


def _num(x):
    try: return float(x) if x is not None else None
    except (TypeError,ValueError): return None

def _avg(values):
    v=[x for x in (_num(x) for x in values) if x is not None]
    return sum(v)/len(v) if v else None

def _higher(x, low, high):
    x=_num(x)
    return None if x is None else max(0,min(100,(x-low)/(high-low)*100))

def _lower(x, good, bad):
    x=_num(x)
    return None if x is None else max(0,min(100,(bad-x)/(bad-good)*100))

def fundamental_score(d: Mapping[str,Any]):
    parts=[_higher(d.get("roe"),0,20),_higher(d.get("roic"),0,15),_higher(d.get("revenue_growth"),-10,20),_higher(d.get("eps_growth"),-10,20),_higher(d.get("fcf_margin"),0,25),_lower(d.get("debt_to_equity"),0,2),_higher(d.get("current_ratio"),0.5,2.0)]
    return _avg(parts)

def valuation_score(d: Mapping[str,Any]):
    parts=[_lower(d.get("pe"),10,35),_lower(d.get("ev_ebitda"),8,30),_higher(d.get("margin_of_safety"),0,40),_higher(d.get("fcf_yield"),0,10),_higher(d.get("peg"),0,2)]
    return _avg(parts)

def technical_score(d: Mapping[str,Any]):
    parts=[_higher(d.get("rsi"),30,70),_higher(d.get("trend_strength"),0,100),_higher(d.get("momentum"),-20,20),_higher(d.get("price_vs_ema200"),-20,20),_higher(d.get("macd_histogram"),-5,5),_higher(d.get("volume_ratio"),0.5,2.0)]
    return _avg(parts)

def risk_score(d: Mapping[str,Any]):
    parts=[_lower(d.get("volatility"),0.10,0.60),_lower(d.get("beta"),0.5,2.0),_lower(d.get("max_drawdown"),0.05,0.60),_higher(d.get("interest_coverage"),1,10),_lower(d.get("debt_to_ebitda"),1,6)]
    return _avg(parts)

def calculate_component_scores(context):
    f=getattr(context,"fundamentals",{}) or {}; v=getattr(context,"valuation",{}) or {}; t=getattr(context,"technical",{}) or {}; r=getattr(context,"risk",{}) or {}
    scores={"fundamental":fundamental_score(f),"valuation":valuation_score(v),"technical":technical_score(t),"risk":risk_score(r)}
    return {k:None if val is None else round(val,2) for k,val in scores.items()}
