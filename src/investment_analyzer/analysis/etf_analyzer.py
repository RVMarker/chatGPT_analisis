"""V12.40 ETF-specific analysis and decision inputs."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from typing import Any

@dataclass(slots=True)
class ETFAnalysis:
    symbol:str
    price:Any=None
    expense_ratio:Any=None
    benchmark:Any=None
    aum:Any=None
    top10:list[dict[str,Any]]=None
    top10_weight:float|None=None
    concentration_score:float|None=None
    coverage:float=0.0
    warnings:list[str]=None
    def as_dict(self): return asdict(self)

class ETFAnalyzer:
    def analyze(self,symbol,payload):
        p=payload or {}; holdings=p.get("holdings") or p.get("topHoldings") or []
        normalized=[]
        if isinstance(holdings,dict):
            for name,weight in holdings.items(): normalized.append({"name":name,"weight":self._weight(weight)})
        elif isinstance(holdings,list):
            for h in holdings:
                if isinstance(h,dict): normalized.append({"name":h.get("name") or h.get("symbol") or h.get("holding"),"weight":self._weight(h.get("weight") if "weight" in h else h.get("percent"))})
        normalized=[x for x in normalized if x["name"]]
        normalized.sort(key=lambda x:x["weight"] if x["weight"] is not None else -1,reverse=True)
        top10=normalized[:10]; top10_weight=sum(x["weight"] or 0 for x in top10) if top10 else None
        concentration=None if top10_weight is None else max(0,min(100,100-top10_weight))
        fields=[p.get("price"),p.get("expense_ratio") or p.get("expenseRatio") or p.get("annualReportExpenseRatio"),p.get("benchmark"),p.get("aum") or p.get("totalAssets"),top10]
        coverage=100*sum(x is not None and x!=[] for x in fields)/len(fields)
        warnings=[]
        if not top10:warnings.append("TOP 10 holdings no disponibles")
        if fields[1] is None:warnings.append("Expense ratio no disponible")
        return ETFAnalysis(symbol,p.get("price"),fields[1],p.get("benchmark"),fields[3],top10,top10_weight,concentration,round(coverage,1),warnings)
    @staticmethod
    def _weight(v):
        if v is None:return None
        try:
            x=float(v)
            return x*100 if 0<=x<=1 else x
        except (TypeError,ValueError):return None
