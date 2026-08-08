"""ETF-specific valuation and composition analysis."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

@dataclass(slots=True)
class ETFHolding:
    rank: int
    ticker: str
    name: str | None
    weight_pct: float

@dataclass(slots=True)
class ETFValuation:
    model: str
    expense_ratio_pct: float | None
    top_10: list[dict[str, Any]]
    top_10_weight_pct: float | None
    nav_per_share: float | None
    premium_discount_pct: float | None
    tracking_difference_pct: float | None
    score: float | None
    warnings: list[str]
    def as_dict(self): return asdict(self)

class ETFValuationEngine:
    def calculate(self, *, holdings=None, expense_ratio=None, nav_per_share=None, current_price=None,
                  premium_discount=None, tracking_difference=None):
        rows=[]
        for i,h in enumerate(holdings or [],1):
            if isinstance(h,dict): ticker=h.get("ticker") or h.get("symbol") or h.get("holding") or "N/D"; name=h.get("name"); weight=h.get("weight_pct",h.get("weight",0))
            else: ticker=getattr(h,"ticker",getattr(h,"symbol","N/D")); name=getattr(h,"name",None); weight=getattr(h,"weight_pct",getattr(h,"weight",0))
            try: weight=float(weight)
            except (TypeError,ValueError): weight=0.0
            rows.append(ETFHolding(i,str(ticker),name,weight))
        rows=sorted(rows,key=lambda x:x.weight_pct,reverse=True)[:10]
        for i,r in enumerate(rows,1): r.rank=i
        top=[asdict(r) for r in rows]
        top_weight=round(sum(r.weight_pct for r in rows),4) if rows else None
        if premium_discount is None and nav_per_share and current_price: premium_discount=(float(current_price)/float(nav_per_share)-1)*100
        warnings=[]
        if not rows: warnings.append("ETF: composición no disponible")
        if expense_ratio is None: warnings.append("ETF: costo de administración (expense ratio) no disponible")
        if nav_per_share is None: warnings.append("ETF: NAV por participación no disponible")
        if tracking_difference is None: warnings.append("ETF: tracking difference no disponible")
        score=None
        if premium_discount is not None:
            score=max(0.0,min(100.0,50.0-abs(float(premium_discount))*10.0))
        return ETFValuation("ETF_NAV_TRACKING", expense_ratio, top, top_weight, nav_per_share, premium_discount, tracking_difference, score, warnings)
