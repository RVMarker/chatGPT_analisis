"""V12.67 REIT/FIBRA-specific valuation using FFO, AFFO and NAV."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from typing import Any,Mapping

@dataclass(slots=True)
class REITFibraAnalysis:
    symbol:str
    price:Any=None
    ffo_share:Any=None
    affo_share:Any=None
    nav_share:Any=None
    distribution_share:Any=None
    ffo_multiple:Any=None
    affo_multiple:Any=None
    nav_premium_discount:Any=None
    payout_on_affo:Any=None
    distribution_yield:Any=None
    debt_ebitda:Any=None
    interest_coverage:Any=None
    occupancy:Any=None
    wale:Any=None
    cap_rate:Any=None
    coverage:float=0.0
    warnings:list[str]=None
    def as_dict(self): return asdict(self)

class REITFibraAnalyzer:
    def analyze(self,symbol:str,payload:Mapping[str,Any]|None=None)->dict[str,Any]:
        p=dict(payload or {})
        price=self._num(p.get('price'))
        ffo=self._num(p.get('ffo_share',p.get('ffoPerShare'))); affo=self._num(p.get('affo_share',p.get('affoPerShare'))); nav=self._num(p.get('nav_share',p.get('navPerShare'))); dist=self._num(p.get('distribution_share',p.get('distributionPerShare')))
        out=REITFibraAnalysis(symbol,price,ffo,affo,nav,dist, self._multiple(price,ffo),self._multiple(price,affo),self._premium(price,nav), self._ratio(dist,affo),self._yield(dist,price),self._num(p.get('debt_ebitda',p.get('debtToEbitda'))),self._num(p.get('interest_coverage',p.get('interestCoverage'))),self._percent(p.get('occupancy')),self._num(p.get('wale')),self._percent(p.get('cap_rate')),0.0,[])
        fields=[price,ffo,affo,nav,dist,out.debt_ebitda,out.interest_coverage,out.occupancy,out.wale,out.cap_rate]; out.coverage=round(100*sum(x is not None for x in fields)/len(fields),1)
        if ffo is None: out.warnings.append('FFO/share no disponible')
        if affo is None: out.warnings.append('AFFO/share no disponible')
        if nav is None: out.warnings.append('NAV/share no disponible')
        return out.as_dict()
    @staticmethod
    def _num(v):
        try:return None if v is None else float(v)
        except (TypeError,ValueError):return None
    @classmethod
    def _multiple(cls,a,b): return None if a is None or b in (None,0) else a/b
    @classmethod
    def _ratio(cls,a,b): return None if a is None or b in (None,0) else a/b*100
    @classmethod
    def _premium(cls,a,b): return None if a is None or b in (None,0) else (a/b-1)*100
    @classmethod
    def _yield(cls,a,b): return None if a is None or b in (None,0) else a/b*100
    @classmethod
    def _percent(cls,v):
        x=cls._num(v); return None if x is None else x*100 if 0<=x<=1 else x
