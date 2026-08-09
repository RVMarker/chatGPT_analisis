"""V12.52 stock valuation: fundamental, DCF, relative valuation, quality and technical separation."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from typing import Any

@dataclass(slots=True)
class StockAnalysis:
    strategic_score:float; tactical_score:float; strategic_coverage:float; tactical_coverage:float
    fair_value:float|None; margin_of_safety:float|None; components:dict[str,dict[str,Any]]; warnings:list[str]
    def as_dict(self): return asdict(self)

class StockDecisionEngine:
    SW={"fundamental":30,"valuation":30,"quality":15,"growth":10,"balance_sheet":10,"dividend":5}
    TW={"technical":35,"momentum":25,"trend":20,"volatility":10,"liquidity":10}
    def analyze(self,*,price=None,dcf_value=None,pe=None,peer_pe=None,peg=None,roe=None,roic=None,revenue_growth=None,earnings_growth=None,debt_equity=None,current_ratio=None,dividend_yield=None,technical=None,momentum=None,trend=None,volatility=None,liquidity=None):
        def n(x): return max(0,min(100,float(x))) if x is not None else None
        warnings=[]; fair=None
        if dcf_value is not None: fair=float(dcf_value)
        elif pe is not None and peer_pe is not None and price is not None and float(pe)!=0: fair=float(price)*float(peer_pe)/float(pe)
        mos=None if fair is None or price in (None,0) else (fair/float(price)-1)*100
        valuation=n(50 if mos is None else 50+mos); fundamental=n((float(roe)*100+float(roic)*100)/2) if roe is not None and roic is not None else n(50+float(earnings_growth or 0)*1.5); quality=n((float(roe)*100+float(roic)*100)/2) if roe is not None and roic is not None else None; growth=n((float(revenue_growth or 0)+float(earnings_growth or 0))*2.5) if revenue_growth is not None or earnings_growth is not None else None; balance=n(100-float(debt_equity)*20) if debt_equity is not None else None; div=n(float(dividend_yield)*20) if dividend_yield is not None else None
        vals={"fundamental":fundamental,"valuation":valuation,"quality":quality,"growth":growth,"balance_sheet":balance,"dividend":div}; tv={"technical":n(technical),"momentum":n(momentum),"trend":n(trend),"volatility":None if volatility is None else n(100-float(volatility)*2),"liquidity":n(liquidity)}
        def calc(vals,weights):
            active=sum(weights[k] for k,v in vals.items() if v is not None); score=sum(weights[k]*v for k,v in vals.items() if v is not None)/active if active else 0; return round(score,2),round(active,2)
        ss,sc=calc(vals,self.SW); ts,tc=calc(tv,self.TW)
        if dcf_value is None and not (pe is not None and peer_pe is not None): warnings.append("Fair value no disponible: faltan DCF o valoración relativa")
        if roe is None or roic is None: warnings.append("ROE/ROIC incompletos: calidad no vota plenamente")
        if technical is None: warnings.append("Technical score ausente")
        return StockAnalysis(ss,ts,sc,tc,None if fair is None else round(fair,4),None if mos is None else round(mos,2),{"strategic":vals,"tactical":tv},warnings)
