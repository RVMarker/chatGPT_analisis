"""V12.51 Bond specialized analysis adapter."""
from __future__ import annotations
from typing import Any
from investment_analyzer.analysis.bond_valuation import BondDecisionEngine

class BondAnalyzer:
    def __init__(self, engine=None): self.engine=engine or BondDecisionEngine()
    def analyze(self,symbol:str,payload:dict[str,Any]|None=None)->dict[str,Any]:
        p=payload or {}
        def first(*keys):
            for k in keys:
                if p.get(k) is not None:return p[k]
            return None
        r=self.engine.analyze(price=first("price","market_price","last_price"),face=first("face","par_value") or 100,coupon_rate=first("coupon_rate","couponRate","coupon"),yield_to_maturity=first("yield_to_maturity","ytm","yield"),maturity_years=first("maturity_years","years_to_maturity"),duration=first("duration","modified_duration"),convexity=first("convexity"),credit_score=first("credit_score","creditScore"),liquidity_score=first("liquidity_score","liquidityScore"),inflation=first("inflation"),spread=first("spread","credit_spread"),momentum=first("momentum"))
        d=r.as_dict(); d["symbol"]=symbol; return d
