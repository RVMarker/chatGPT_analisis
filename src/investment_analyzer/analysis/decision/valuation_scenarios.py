"""V12.93 scenario-based valuation and target derivation."""
from __future__ import annotations
from typing import Any, Mapping


def _num(v):
    try:
        x=float(v)
        return x if x>0 else None
    except (TypeError,ValueError): return None

class ValuationScenarioEngine:
    def build(self, data: Mapping[str, Any], price: float|None=None) -> dict[str,Any]:
        price=_num(price or data.get('price') or data.get('current_price'))
        fair=_num(data.get('fair_value') or data.get('intrinsic_value') or data.get('dcf_fair_value'))
        bear=_num(data.get('bear_value') or data.get('bear_case'))
        bull=_num(data.get('bull_value') or data.get('bull_case'))
        if fair is None:
            vals=[_num(data.get(k)) for k in ('dcf_fair_value','graham_value','peg_value','relative_value')]
            vals=[x for x in vals if x is not None]
            fair=sum(vals)/len(vals) if vals else None
        if fair is not None:
            bear=bear or fair*0.80; bull=bull or fair*1.20
        mos=(fair-price)/fair if fair and price else None
        return {'price':price,'bear_value':round(bear,4) if bear else None,'base_fair_value':round(fair,4) if fair else None,'bull_value':round(bull,4) if bull else None,'margin_of_safety_pct':round(mos*100,2) if mos is not None else None,'available':fair is not None,'method':'provided_or_average_of_available_valuation_methods'}
