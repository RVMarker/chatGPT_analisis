"""V12.72 fixed-income analyzer for bonds, CETES and UDIBONOS."""
from __future__ import annotations
from typing import Any,Mapping

class BondAnalyzer:
    def analyze(self,symbol:str,payload:Mapping[str,Any]|None=None)->dict[str,Any]:
        p=dict(payload or {}); price=self._num(p.get('price')); face=self._num(p.get('face_value',p.get('par_value',100))); coupon=self._num(p.get('coupon_rate',p.get('coupon'))); ytm=self._num(p.get('ytm',p.get('yield_to_maturity',p.get('yield')))); maturity=self._num(p.get('years_to_maturity',p.get('maturity_years'))); duration=self._num(p.get('modified_duration',p.get('duration_modified',p.get('duration')))); convexity=self._num(p.get('convexity')); spread=self._num(p.get('credit_spread',p.get('spread'))); benchmark=self._num(p.get('benchmark_yield',p.get('reference_yield')))
        coupon_pct=self._pct(coupon); ytm_pct=self._pct(ytm); spread_bp=None if spread is None else spread*10000 if abs(spread)<1 else spread
        sensitivity=None if duration is None else -duration
        price_change_100bp=None if duration is None else -duration + .5*(convexity or 0)*.01
        real_yield=None
        inflation=self._num(p.get('inflation')); inflation_pct=self._pct(inflation)
        if ytm_pct is not None and inflation_pct is not None: real_yield=(1+ytm_pct/100)/(1+inflation_pct/100)-1
        rate_gap=None if ytm_pct is None or benchmark is None else ytm_pct-self._pct(benchmark)
        coverage=100*sum(x is not None for x in [price,coupon_pct,ytm_pct,maturity,duration,convexity,spread_bp])/7
        warnings=[]
        if ytm_pct is None:warnings.append('YTM no disponible')
        if duration is None:warnings.append('Duración no disponible')
        if maturity is None:warnings.append('Vencimiento no disponible')
        return {'symbol':symbol,'price':price,'face_value':face,'coupon_rate':coupon_pct,'ytm':ytm_pct,'years_to_maturity':maturity,'duration':duration,'convexity':convexity,'credit_spread_bps':spread_bp,'benchmark_yield':self._pct(benchmark),'yield_spread_vs_benchmark':rate_gap,'rate_sensitivity_per_100bp':sensitivity,'estimated_price_change_100bp_pct':price_change_100bp,'real_yield':None if real_yield is None else real_yield*100,'coverage':round(coverage,1),'warnings':warnings}
    @staticmethod
    def _num(v):
        try:return None if v is None else float(v)
        except (TypeError,ValueError):return None
    @classmethod
    def _pct(cls,v):
        x=cls._num(v); return None if x is None else x*100 if 0<=x<=1 else x
