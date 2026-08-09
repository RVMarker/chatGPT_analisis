"""V12.95 risk-aware trade plan: entry, SL, targets, scenarios and R/R."""
from __future__ import annotations
from typing import Any

class RiskTradePlan:
    def build(self, *, price: float|None, fair_value: float|None=None,
              bear_value: float|None=None, bull_value: float|None=None,
              technical_support: float|None=None, technical_resistance: float|None=None,
              atr: float|None=None, atr_stop_mult: float=2.0,
              risk_pct: float=0.02, target_pct: float|None=None) -> dict[str,Any]:
        if price is None or price <= 0:
            return {'status':'INSUFFICIENT_DATA','stop_loss':None,'target_1':None,'target_2':None,'risk_reward':None}
        p=float(price)
        candidates=[]
        if technical_support is not None and 0 < technical_support < p: candidates.append(float(technical_support))
        if atr is not None and atr > 0 and p-float(atr)*atr_stop_mult > 0: candidates.append(p-float(atr)*atr_stop_mult)
        sl=max(candidates) if candidates else p*(1-risk_pct)
        sl=min(sl,p*0.999)
        t1=float(technical_resistance) if technical_resistance is not None and technical_resistance > p else None
        t2=float(fair_value) if fair_value is not None and fair_value > p else None
        if target_pct is not None and target_pct > 0:
            candidate=p*(1+float(target_pct)); t1=t1 or candidate; t2=t2 or candidate
        if t1 is None and t2 is None: t1=p*(1+max(risk_pct,0.05))
        if t2 is None: t2=t1
        # Target 2 may not exceed the bull valuation without an explicit external override.
        if bull_value is not None and bull_value > p and t2 is not None: t2=min(t2,float(bull_value))
        if t1 is not None and t2 is not None and t1 >= t2: t1=None
        risk=p-sl; reward=max(x for x in (t1,t2) if x is not None)-p if any(x is not None for x in (t1,t2)) else 0
        rr=reward/risk if risk>0 and reward>0 else None
        return {'status':'OK','entry':round(p,6),'stop_loss':round(sl,6),'target_1':round(t1,6) if t1 is not None else None,'target_2':round(t2,6) if t2 is not None else None,'bear_value':bear_value,'base_fair_value':fair_value,'bull_value':bull_value,'risk_amount_per_unit':round(risk,6),'reward_amount_per_unit':round(reward,6),'risk_reward':round(rr,2) if rr is not None else None,'risk_pct':round(risk/p*100,2),'upside_to_target_pct':round(reward/p*100,2),'upside_to_fair_value_pct':round((float(fair_value)/p-1)*100,2) if fair_value is not None and fair_value>0 else None,'method':{'stop':'support_or_ATR_or_risk_fallback','target_1':'resistance','target_2':'fair_value_capped_by_bull','bull_cap':bull_value}}
