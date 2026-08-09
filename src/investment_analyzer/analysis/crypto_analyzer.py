"""V12.70 crypto-specific market, liquidity, supply and risk analysis."""
from __future__ import annotations
from typing import Any,Mapping

class CryptoAnalyzer:
    def analyze(self,symbol:str,payload:Mapping[str,Any]|None=None)->dict[str,Any]:
        p=dict(payload or {})
        market_cap=self._num(p.get('market_cap',p.get('marketCap'))); volume=self._num(p.get('volume_24h',p.get('volume24h'))); price=self._num(p.get('price',p.get('current_price')))
        supply=self._num(p.get('circulating_supply',p.get('circulatingSupply'))); max_supply=self._num(p.get('max_supply',p.get('maxSupply'))); drawdown=self._num(p.get('max_drawdown',p.get('maxDrawdown')))
        volatility=self._num(p.get('volatility',p.get('annualized_volatility'))); dominance=self._num(p.get('market_dominance',p.get('dominance')))
        turnover=None if market_cap in (None,0) or volume is None else volume/market_cap*100
        supply_ratio=None if supply in (None,0) or max_supply in (None,0) else supply/max_supply*100
        liquidity_score=None if turnover is None else max(0,min(100,turnover*20))
        risk=50.0
        if drawdown is not None: risk += min(30,max(-30,abs(drawdown)*.25))
        if volatility is not None: risk += min(20,max(-20,volatility*.10))
        risk=min(100,max(0,risk))
        warnings=[]
        if market_cap is None:warnings.append('Market cap no disponible')
        if volume is None:warnings.append('Volumen 24h no disponible')
        if supply is None:warnings.append('Circulating supply no disponible')
        return {'symbol':symbol,'price':price,'market_cap':market_cap,'volume_24h':volume,'circulating_supply':supply,'max_supply':max_supply,'supply_ratio':supply_ratio,'market_dominance':dominance,'volume_market_cap_pct':turnover,'max_drawdown':drawdown,'volatility':volatility,'liquidity_score':liquidity_score,'risk_score':round(risk,2),'warnings':warnings}
    @staticmethod
    def _num(v):
        try:return None if v is None else float(v)
        except (TypeError,ValueError):return None
