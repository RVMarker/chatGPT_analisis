"""V12.48 crypto strategic/tactical scoring with explicit coverage."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from typing import Any

@dataclass(slots=True)
class CryptoAnalysis:
    strategic_score:float; tactical_score:float; strategic_coverage:float; tactical_coverage:float
    components:dict[str,dict[str,Any]]; warnings:list[str]
    def as_dict(self): return asdict(self)

class CryptoDecisionEngine:
    STRATEGIC={"market_quality":20,"supply":15,"liquidity":15,"risk":25,"onchain":15,"valuation":10}
    TACTICAL={"momentum":30,"volatility":20,"liquidity":20,"flow":15,"trend":15}
    def analyze(self, *, market_cap=None,volume_24h=None,circulating_supply=None,max_supply=None,total_supply=None,volatility=None,max_drawdown=None,onchain_score=None,valuation_score=None,momentum=None,trend=None,exchange_flow=None,smart_money=None):
        w={}; s={}; t={}; warnings=[]
        def norm(x): return max(0,min(100,float(x))) if x is not None else None
        mc=norm(min(100,float(market_cap)/1e11*100)) if market_cap is not None else None
        liq=norm(min(100,float(volume_24h)/1e9*100)) if volume_24h is not None else None
        supply=50 if circulating_supply is None or max_supply in (None,0) else norm(float(circulating_supply)/float(max_supply)*100)
        risk=None if volatility is None and max_drawdown is None else norm(100-(float(volatility or 0)*2)-(abs(float(max_drawdown or 0))*0.5))
        on=norm(onchain_score); val=norm(valuation_score); mom=norm(momentum); tr=norm(trend); flow=norm(exchange_flow if exchange_flow is not None else smart_money)
        def calc(vals,weights):
            active=sum(weights[k] for k,v in vals.items() if v is not None); score=sum(weights[k]*v for k,v in vals.items() if v is not None)/active if active else 0
            return round(score,2),round(active,2)
        svals={"market_quality":mc,"supply":supply,"liquidity":liq,"risk":risk,"onchain":on,"valuation":val}; tvals={"momentum":mom,"volatility":None if volatility is None else norm(100-float(volatility)*2),"liquidity":liq,"flow":flow,"trend":tr}
        ss,sc=calc(svals,self.STRATEGIC); ts,tc=calc(tvals,self.TACTICAL)
        if market_cap is None:warnings.append("Market cap ausente")
        if volume_24h is None:warnings.append("Volumen 24h ausente")
        if onchain_score is None:warnings.append("On-chain no disponible: no vota estratégicamente")
        if valuation_score is None:warnings.append("Valoración fundamental crypto no disponible: no vota estratégicamente")
        if exchange_flow is None and smart_money is None:warnings.append("Flujos/smart money no disponibles: no votan tácticamente")
        return CryptoAnalysis(ss,ts,sc,tc,{"strategic":svals,"tactical":tvals},warnings)
