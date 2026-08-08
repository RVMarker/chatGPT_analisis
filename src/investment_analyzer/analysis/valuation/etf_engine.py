"""ETF-specific quality, benchmark, composition and cost analysis."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

@dataclass(slots=True)
class ETFHolding:
    rank:int; ticker:str; name:str|None; weight_pct:float

@dataclass(slots=True)
class ETFValuation:
    model:str; category:str|None; benchmark:str|None; expense_ratio_pct:float|None
    top_10:list[dict[str,Any]]; top_10_weight_pct:float|None
    concentration_score:float|None; diversification_score:float|None; expense_score:float|None
    tracking_score:float|None; nav_score:float|None; performance_score:float|None
    quality_score:float|None; nav_per_share:float|None; premium_discount_pct:float|None
    tracking_difference_pct:float|None; tracking_error_pct:float|None
    sector_concentration_pct:float|None; geography_concentration_pct:float|None
    category_expense_ratio_pct:float|None; dividend_yield_pct:float|None
    distribution_frequency:str|None; benchmark_return_pct:float|None; etf_return_pct:float|None
    relative_return_pct:float|None; score:float|None; warnings:list[str]
    def as_dict(self): return asdict(self)

class ETFValuationEngine:
    def calculate(self, *, holdings=None, expense_ratio=None, nav_per_share=None, current_price=None,
                  premium_discount=None, tracking_difference=None, tracking_error=None,
                  sector_concentration=None, geography_concentration=None, category_expense_ratio=None,
                  benchmark=None, category=None, benchmark_return=None, etf_return=None,
                  dividend_yield=None, distribution_frequency=None):
        rows=[]
        for h in holdings or []:
            if isinstance(h,dict): ticker=h.get("ticker") or h.get("symbol") or h.get("holding") or "N/D"; name=h.get("name"); weight=h.get("weight_pct",h.get("weight",0))
            else: ticker=getattr(h,"ticker",getattr(h,"symbol","N/D")); name=getattr(h,"name",None); weight=getattr(h,"weight_pct",getattr(h,"weight",0))
            try: weight=float(weight)
            except (TypeError,ValueError): weight=0.0
            rows.append(ETFHolding(0,str(ticker),name,weight))
        rows=sorted(rows,key=lambda x:x.weight_pct,reverse=True)[:10]
        for i,r in enumerate(rows,1): r.rank=i
        top=[asdict(r) for r in rows]; top_weight=round(sum(r.weight_pct for r in rows),4) if rows else None
        if premium_discount is None and nav_per_share and current_price: premium_discount=(float(current_price)/float(nav_per_share)-1)*100
        relative_return=None if benchmark_return is None or etf_return is None else float(etf_return)-float(benchmark_return)
        warnings=[]
        checks=((not rows,"ETF: composición no disponible"),(expense_ratio is None,"ETF: costo de administración (expense ratio) no disponible"),(nav_per_share is None,"ETF: NAV por participación no disponible"),(tracking_difference is None,"ETF: tracking difference no disponible"),(tracking_error is None,"ETF: tracking error no disponible"),(sector_concentration is None,"ETF: concentración sectorial no disponible"),(geography_concentration is None,"ETF: concentración geográfica no disponible"),(benchmark is None,"ETF: benchmark no disponible"))
        warnings += [msg for missing,msg in checks if missing]
        concentration_score=None if top_weight is None else (100.0 if top_weight<=35 else max(0.0,min(100.0,100-(top_weight-35)*2.5)))
        diversification_score=None
        if concentration_score is not None and sector_concentration is not None and geography_concentration is not None:
            diversification_score=round((concentration_score+(100-max(0,min(100,float(sector_concentration))))+(100-max(0,min(100,float(geography_concentration)))))/3,2)
        expense_score=None
        if expense_ratio is not None:
            er=float(expense_ratio); expense_score=100 if er<=.10 else max(0,min(100,100-(er-.10)*100))
            if category_expense_ratio and float(category_expense_ratio)>0: expense_score=max(0,min(100,70+(float(category_expense_ratio)-er)/float(category_expense_ratio)*30))
        tracking_score=None
        if tracking_difference is not None or tracking_error is not None:
            td=abs(float(tracking_difference or 0)); te=abs(float(tracking_error or 0)); tracking_score=max(0,min(100,100-(td*60+te*40)))
        nav_score=None if premium_discount is None else max(0,min(100,100-abs(float(premium_discount))*20))
        performance_score=None
        if relative_return is not None: performance_score=max(0,min(100,50+relative_return*10))
        components=[x for x in (diversification_score,expense_score,tracking_score,nav_score,performance_score) if x is not None]
        quality_score=round(sum(components)/len(components),2) if components else None
        return ETFValuation("ETF_NAV_TRACKING",category,benchmark,expense_ratio,top,top_weight,concentration_score,diversification_score,expense_score,tracking_score,nav_score,performance_score,quality_score,nav_per_share,premium_discount,tracking_difference,tracking_error,sector_concentration,geography_concentration,category_expense_ratio,dividend_yield,distribution_frequency,benchmark_return,etf_return,relative_return,quality_score,warnings)
