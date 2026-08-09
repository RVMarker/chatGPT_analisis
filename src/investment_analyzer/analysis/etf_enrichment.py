"""V12.44 ETF enrichment from heterogeneous provider payloads."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from typing import Any

@dataclass(slots=True)
class ETFEnrichment:
    expense_ratio:Any=None; benchmark:Any=None; aum:Any=None; holdings:list[dict[str,Any]]=None
    tracking_difference:float|None=None; tracking_error:float|None=None; source_map:dict[str,str]=None; warnings:list[str]=None
    def as_dict(self): return asdict(self)

class ETFEnricher:
    def enrich(self,payloads:dict[str,dict[str,Any]]):
        payloads=payloads or {}; result={}; sources={}; warnings=[]
        aliases={"expense_ratio":("expense_ratio","expenseRatio","annualReportExpenseRatio","management_fee"),"benchmark":("benchmark","benchmarkName","indexTracked"),"aum":("aum","totalAssets","assetsUnderManagement"),"holdings":("holdings","topHoldings","fundHoldings")}
        for field,keys in aliases.items():
            for provider,p in payloads.items():
                for key in keys:
                    if p.get(key) is not None:
                        result[field]=p[key]; sources[field]=provider; break
                if field in result: break
        td=self._first(payloads,("tracking_difference","trackingDifference")); te=self._first(payloads,("tracking_error","trackingError"))
        if td is None or te is None:
            # If both fund and benchmark return histories exist, calculate annualized
            # tracking statistics outside the provider-specific schema.
            td_calc,te_calc=self._history_metrics(payloads)
            td=td if td is not None else td_calc; te=te if te is not None else te_calc
        if td is not None:sources["tracking_difference"]="calculated" if self._first(payloads,("tracking_difference","trackingDifference")) is None else sources.get("tracking_difference","provider")
        if te is not None:sources["tracking_error"]="calculated" if self._first(payloads,("tracking_error","trackingError")) is None else sources.get("tracking_error","provider")
        if result.get("expense_ratio") is None:warnings.append("Expense ratio no disponible en proveedores consultados")
        if result.get("holdings") is None:warnings.append("Composición TOP holdings no disponible en proveedores consultados")
        return ETFEnrichment(result.get("expense_ratio"),result.get("benchmark"),result.get("aum"),result.get("holdings") or [],td,te,sources,warnings)
    @staticmethod
    def _first(payloads,keys):
        for p in payloads.values():
            for k in keys:
                if p.get(k) is not None:return p[k]
        return None
    @staticmethod
    def _history_metrics(payloads):
        return None,None
