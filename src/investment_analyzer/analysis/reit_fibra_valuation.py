"""V12.68 REIT/FIBRA valuation: FFO/AFFO/NAV fair value and transparent strategic verdict."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from typing import Any

@dataclass(slots=True)
class REITValuation:
    model:str
    fair_value:float|None
    score:float
    coverage:float
    margin_of_safety:float|None
    components:dict[str,dict[str,Any]]
    context:dict[str,Any]
    warnings:list[str]
    strategic_verdict:str='HOLD'
    def as_dict(self): return asdict(self)

class REITFibraValuation:
    WEIGHTS={"ffo_value":35.0,"affo_value":25.0,"nav_value":15.0,"distribution_quality":10.0,"leverage":10.0,"interest_coverage":5.0}
    def evaluate(self, *, price:float|None, ffo_share:float|None=None, affo_share:float|None=None, nav_share:float|None=None, distribution_share:float|None=None, payout_ffo:float|None=None, net_debt_ebitda:float|None=None, interest_coverage:float|None=None, cap_rate:float|None=None, ffo_multiple:float=17.0, affo_multiple:float=16.0, required_return:float=0.085, **kwargs):
        warnings=[]; comps={}; values=[]; fair_candidates=[]
        def add(name,score):
            if score is not None: comps[name]={"score":round(max(0,min(100,score)),2),"weight":self.WEIGHTS[name]}; values.append((name,comps[name]["score"]))
        if ffo_share is not None:
            fv=float(ffo_share)*ffo_multiple; fair_candidates.append(fv); add("ffo_value",self._valuation_score(fv,price))
        if affo_share is not None:
            fv=float(affo_share)*affo_multiple; fair_candidates.append(fv); add("affo_value",self._valuation_score(fv,price))
        if nav_share is not None:
            fv=float(nav_share); fair_candidates.append(fv); add("nav_value",self._valuation_score(fv,price))
        if distribution_share is not None:
            payout=100 if payout_ffo is None else max(0,min(100,float(payout_ffo)*100)); add("distribution_quality",100-abs(payout-70)*1.4)
        if net_debt_ebitda is not None: add("leverage",100-(max(0,float(net_debt_ebitda)-4)*15))
        if interest_coverage is not None: add("interest_coverage",min(100,max(0,float(interest_coverage)*20)))
        active=sum(self.WEIGHTS[k] for k,_ in values); score=sum(self.WEIGHTS[k]*v for k,v in values)/active if active else 0
        for k in comps: comps[k]["contribution"]=round(self.WEIGHTS[k]*comps[k]["score"]/active*100,2) if active else 0
        fair_value=sum(fair_candidates)/len(fair_candidates) if fair_candidates else None
        mos=None if fair_value is None or price in (None,0) else (fair_value/float(price)-1)*100
        verdict='BUY' if score>=65 and (mos is None or mos>=10) else 'SELL' if score<40 or (mos is not None and mos<-10) else 'HOLD'
        if not fair_candidates:warnings.append('Sin FFO/AFFO/NAV: no se puede calcular fair value específico')
        if ffo_share is None:warnings.append('FFO/share ausente')
        if affo_share is None:warnings.append('AFFO/share ausente')
        if nav_share is None:warnings.append('NAV/share ausente')
        context={'payout_ffo':payout_ffo,'cap_rate':cap_rate,'required_return':required_return,'p_e':'CONTEXTO; no vota en valoración REIT/FIBRA','ev_ebitda':'CONTEXTO; no vota salvo benchmark sectorial'}
        return REITValuation('FFO_AFFO_NAV',None if fair_value is None else round(fair_value,4),round(score,2),round(active,2),None if mos is None else round(mos,2),comps,context,warnings,verdict)
    @staticmethod
    def _valuation_score(fair_value,price):
        if price in (None,0): return 50
        return max(0,min(100,50+(float(fair_value)/float(price)-1)*100))
