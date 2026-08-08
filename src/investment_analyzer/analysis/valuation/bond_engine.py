"""Bond-specific valuation and rate/credit risk analysis."""
from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass(slots=True)
class BondValuation:
    model:str; price:float|None; face_value:float|None; coupon_rate_pct:float|None; ytm_pct:float|None
    maturity_years:float|None; duration:float|None; modified_duration:float|None; convexity:float|None
    spread_bps:float|None; credit_rating:str|None; real_yield_pct:float|None
    benchmark_yield_pct:float|None; yield_spread_bps:float|None; rate_risk_score:float|None
    credit_score:float|None; value_score:float|None; total_score:float|None; warnings:list[str]
    def as_dict(self): return asdict(self)

class BondValuationEngine:
    def calculate(self, *, price=None, face_value=None, coupon_rate=None, ytm=None, maturity_years=None,
                  duration=None, modified_duration=None, convexity=None, spread_bps=None,
                  credit_rating=None, inflation=None, benchmark_yield=None, benchmark_name=None):
        if modified_duration is None and duration is not None and ytm is not None:
            modified_duration=float(duration)/(1+float(ytm)/100)
        real_yield=None if ytm is None or inflation is None else (1+float(ytm)/100)/(1+float(inflation)/100)*100-100
        yield_spread=None if ytm is None or benchmark_yield is None else (float(ytm)-float(benchmark_yield))*100
        warnings=[]
        for value,msg in ((price,"precio"),(ytm,"YTM"),(maturity_years,"vencimiento"),(duration,"duración"),(credit_rating,"rating")):
            if value is None: warnings.append(f"BOND: {msg} no disponible")
        rate_score=None if modified_duration is None else max(0,min(100,100-float(modified_duration)*8))
        credit_score=None
        if credit_rating:
            rating=str(credit_rating).upper().replace(" ","")
            scale={"AAA":100,"AA+":95,"AA":92,"AA-":89,"A+":85,"A":82,"A-":78,"BBB+":72,"BBB":68,"BBB-":64,"BB+":55,"BB":48,"BB-":42,"B+":35,"B":28,"B-":22,"CCC":10}
            credit_score=scale.get(rating)
        value_score=None if yield_spread is None else max(0,min(100,50+yield_spread*2))
        comps=[x for x in (rate_score,credit_score,value_score) if x is not None]
        total=round(sum(comps)/len(comps),2) if comps else None
        return BondValuation("BOND_YTM_DURATION_CREDIT",price,face_value,coupon_rate,ytm,maturity_years,duration,modified_duration,convexity,spread_bps,credit_rating,real_yield,benchmark_yield,yield_spread,rate_score,credit_score,value_score,total,warnings)
