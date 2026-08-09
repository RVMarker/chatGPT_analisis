"""V12.83 risk-aware trade plan: stop loss, targets and risk/reward."""
from __future__ import annotations
from typing import Any

class RiskTradePlan:
    def build(self, *, price: float|None, fair_value: float|None=None,
              technical_support: float|None=None, technical_resistance: float|None=None,
              atr: float|None=None, atr_stop_mult: float=2.0,
              risk_pct: float=0.02, target_pct: float|None=None) -> dict[str,Any]:
        if price is None or price <= 0:
            return {'status':'INSUFFICIENT_DATA','stop_loss':None,'target_1':None,'target_2':None,'risk_reward':None}
        p=float(price)
        candidates=[]
        if technical_support is not None and 0 < technical_support < p: candidates.append(float(technical_support))
        if atr is not None and atr > 0: candidates.append(p-float(atr)*atr_stop_mult)
        sl=max(candidates) if candidates else p*(1-risk_pct)
        sl=min(sl,p*0.999)
        t1=None; t2=None
        if technical_resistance is not None and technical_resistance > p: t1=float(technical_resistance)
        if fair_value is not None and fair_value > p: t2=float(fair_value)
        if target_pct is not None and target_pct > 0:
            candidate=p*(1+float(target_pct)); t1=t1 or candidate; t2=t2 or candidate
        if t1 is None and t2 is None: t1=p*(1+max(risk_pct,0.05))
        if t2 is None: t2=t1
        risk=p-sl; reward=max(t1,t2)-p; rr=reward/risk if risk>0 else None
        return {'status':'OK','entry':round(p,6),'stop_loss':round(sl,6),'target_1':round(t1,6),'target_2':round(t2,6),'risk_amount_per_unit':round(risk,6),'reward_amount_per_unit':round(reward,6),'risk_reward':round(rr,2) if rr is not None else None,'risk_pct':round(risk/p*100,2),'upside_to_target_pct':round(reward/p*100,2),'upside_to_fair_value_pct':round((float(fair_value)/p-1)*100,2) if fair_value is not None else None,'method':{'stop':'support_or_ATR','target_1':'resistance_or_fallback','target_2':'fair_value_or_target_1'}}
