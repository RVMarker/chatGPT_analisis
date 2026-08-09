"""V12.96 decision quality gate.
Separates asset quality from whether the current entry is executable.
"""
from __future__ import annotations
from typing import Any

class DecisionQualityGate:
    def evaluate(self, *, strategic_verdict: str|None, tactical_verdict: str|None,
                 score: float|None, fair_value: float|None, price: float|None,
                 risk_reward: float|None, margin_of_safety: float|None,
                 stop_loss: float|None = None, target_1: float|None = None,
                 target_2: float|None = None, data_coverage: float|None = None,
                 min_rr: float = 2.0, min_mos: float = 0.10) -> dict[str, Any]:
        reasons=[]
        if price is None or price <= 0:
            return {'status':'INSUFFICIENT_DATA','operation':'ESPERAR','reasons':['Precio actual no disponible']}
        p=float(price)
        upside=(float(fair_value)/p-1.0) if fair_value is not None and fair_value>0 else None
        mos=float(margin_of_safety) if margin_of_safety is not None else upside
        score_ok=score is not None and float(score)>=65
        valuation_ok=upside is not None and upside>=float(min_mos)
        rr_ok=risk_reward is not None and float(risk_reward)>=float(min_rr)
        trade_plan_ok=stop_loss is not None and float(stop_loss)<p and target_1 is not None and float(target_1)>p and target_2 is not None and float(target_2)>p
        coverage_ok=data_coverage is None or float(data_coverage)>=70
        if not score_ok: reasons.append('Score estratégico inferior a 65')
        if not valuation_ok: reasons.append('Margen de seguridad insuficiente o Fair Value no disponible')
        if not rr_ok: reasons.append(f'R/R no disponible o inferior a {min_rr:.1f}')
        if not trade_plan_ok: reasons.append('Plan operativo incompleto: se requieren SL, Target 1 y Target 2')
        if not coverage_ok: reasons.append('Cobertura de datos inferior a 70%')
        if strategic_verdict in {'VENDER','REDUCIR'}: reasons.append(f'Veredicto estratégico: {strategic_verdict}')
        operation='COMPRAR' if not reasons else ('VENDER' if strategic_verdict in {'VENDER','REDUCIR'} and not score_ok else 'ESPERAR')
        return {'status':'OK','operation':operation,'reasons':reasons,'entry':p,'fair_value':fair_value,'upside_to_fair_value_pct':round(upside*100,2) if upside is not None else None,'margin_of_safety_pct':round(mos*100,2) if mos is not None else None,'risk_reward':round(float(risk_reward),2) if risk_reward is not None else None,'stop_loss':stop_loss,'target_1':target_1,'target_2':target_2,'strategic_verdict':strategic_verdict,'tactical_verdict':tactical_verdict,'score':score,'data_coverage':data_coverage,'thresholds':{'min_score':65,'min_rr':min_rr,'min_margin_of_safety':min_mos,'min_coverage':70}}
