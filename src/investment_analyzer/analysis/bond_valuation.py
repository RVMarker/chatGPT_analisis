"""V12.50 bond valuation, duration, convexity and credit risk."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from typing import Any

@dataclass(slots=True)
class BondAnalysis:
    strategic_score:float; tactical_score:float; strategic_coverage:float; tactical_coverage:float
    fair_price:float|None; rate_sensitivity:float|None; components:dict[str,dict[str,Any]]; warnings:list[str]
    def as_dict(self): return asdict(self)

class BondDecisionEngine:
    SW={"valuation":30,"credit":25,"duration":15,"cashflow":15,"liquidity":10,"inflation":5}
    TW={"yield":30,"rate_sensitivity":25,"spread":20,"momentum":15,"liquidity":10}
    def analyze(self,*,price=None,face=100,coupon_rate=None,yield_to_maturity=None,maturity_years=None,duration=None,convexity=None,credit_score=None,liquidity_score=None,inflation=None,spread=None,momentum=None):
        warnings=[]
        def n(x): return max(0,min(100,float(x))) if x is not None else None
        y=n(100-(float(yield_to_maturity or 0)*100)) if yield_to_maturity is not None else None
        credit=n(credit_score); liq=n(liquidity_score); inf=n(100-float(inflation)*10) if inflation is not None else None
        dur=None if duration is None else n(100-float(duration)*8); spr=n(100-float(spread)*10) if spread is not None else None; mom=n(momentum)
        rs=None if duration is None else n(100-float(duration)*8)
        fair=None
        if coupon_rate is not None and yield_to_maturity is not None and maturity_years is not None:
            c=float(face)*float(coupon_rate); r=float(yield_to_maturity); m=int(maturity_years)
            fair=c*(1-(1+r)**(-m))/r+float(face)*(1+r)**(-m) if r else c*m+float(face)
        vals={"valuation":None if fair is None or price is None else n(50+(fair/float(price)-1)*100),"credit":credit,"duration":dur,"cashflow":n(100-abs(float(coupon_rate or 0)*100- float(yield_to_maturity or 0)*100)*3) if coupon_rate is not None and yield_to_maturity is not None else None,"liquidity":liq,"inflation":inf}
        tv={"yield":y,"rate_sensitivity":rs,"spread":spr,"momentum":mom,"liquidity":liq}
        def calc(vals,weights):
            active=sum(weights[k] for k,v in vals.items() if v is not None); score=sum(weights[k]*v for k,v in vals.items() if v is not None)/active if active else 0
            return round(score,2),round(active,2)
        ss,sc=calc(vals,self.SW); ts,tc=calc(tv,self.TW)
        if fair is None:warnings.append("Fair value de bono no calculable: faltan cupón, YTM o vencimiento")
        if duration is None:warnings.append("Duration ausente: sensibilidad a tasas no disponible")
        if credit_score is None:warnings.append("Credit score ausente")
        return BondAnalysis(ss,ts,sc,tc,None if fair is None else round(fair,4),None if duration is None else round(-float(duration),4),{"strategic":vals,"tactical":tv},warnings)
