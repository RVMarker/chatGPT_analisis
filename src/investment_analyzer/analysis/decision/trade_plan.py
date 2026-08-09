"""V12.94 operational trade plan.

Separates analytical conviction from executable trade eligibility.
"""
from __future__ import annotations
from typing import Any


def _p(v):
    try:
        x=float(v)
        return x if x>0 else None
    except (TypeError,ValueError): return None

class TradePlanEngine:
    def build(self, *, price, fair_value=None, bear_value=None, bull_value=None,
              support=None, resistance=None, atr=None, capital=5000.0,
              risk_pct=.02, max_position_pct=.25, min_rr=2.0,
              tactical_score=None, strategic_score=None, min_mos_pct=10.0):
        price=_p(price); fair=_p(fair_value); bear=_p(bear_value); bull=_p(bull_value)
        support=_p(support); resistance=_p(resistance); atr=_p(atr)
        capital=_p(capital) or 0; risk_pct=max(0,float(risk_pct)); max_position_pct=max(0,float(max_position_pct)); min_rr=max(0,float(min_rr))
        if not price: return {'available':False,'operation':'ESPERAR','reasons':['Precio actual no disponible']}
        # Prefer market structure support; ATR is fallback. Never place SL above entry.
        sl=support if support and support<price else (price-2*atr if atr and price-2*atr>0 else None)
        # Target 1 is the first credible resistance below base value; target 2 is base fair value, capped by bull.
        t1=resistance if resistance and resistance>price else None
        if fair and fair>price: t2=fair
        elif bull and bull>price: t2=bull
        else: t2=None
        if bull and t2: t2=min(t2,bull)
        if t1 and t2 and t1>=t2: t1=None
        mos=((fair-price)/fair*100) if fair else None
        risk_per_unit=(price-sl) if sl else None
        rr=((t2-price)/risk_per_unit) if t2 and risk_per_unit and risk_per_unit>0 else None
        risk_budget=capital*risk_pct
        max_position=capital*max_position_pct
        units_by_risk=int(risk_budget/risk_per_unit) if risk_per_unit and risk_per_unit>0 else 0
        units_by_capital=int(max_position/price) if price>0 else 0
        units=max(0,min(units_by_risk,units_by_capital))
        position_value=units*price; actual_risk=units*risk_per_unit if risk_per_unit else None
        reasons=[]
        if not sl: reasons.append('Stop Loss no disponible')
        if not t2: reasons.append('Target no disponible')
        if mos is not None and mos<min_mos_pct: reasons.append(f'Margin of Safety inferior a {min_mos_pct:.1f}%')
        if rr is not None and rr<min_rr: reasons.append(f'R/R inferior a {min_rr:.1f}')
        if strategic_score is not None and float(strategic_score)<60: reasons.append('Score estratégico insuficiente')
        if tactical_score is not None and float(tactical_score)<50: reasons.append('Score táctico insuficiente')
        if units<=0: reasons.append('Tamaño de posición no permitido por riesgo/capital')
        operation='COMPRAR' if not reasons else 'ESPERAR'
        return {'available':bool(sl and t2),'operation':operation,'reasons':reasons,'entry':price,'stop_loss':sl,'target_1':t1,'target_2':t2,'bear_value':bear,'base_fair_value':fair,'bull_value':bull,'margin_of_safety_pct':mos,'risk_per_unit':risk_per_unit,'risk_budget':risk_budget,'units':units,'position_value':position_value,'actual_risk':actual_risk,'actual_risk_pct':(actual_risk/capital*100 if actual_risk is not None and capital else None),'risk_reward':rr,'min_risk_reward':min_rr}
