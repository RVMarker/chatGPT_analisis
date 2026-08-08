"""ETF-specific quality, composition and valuation analysis."""
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
    concentration_score: float | None
    diversification_score: float | None
    expense_score: float | None
    tracking_score: float | None
    nav_score: float | None
    quality_score: float | None
    nav_per_share: float | None
    premium_discount_pct: float | None
    tracking_difference_pct: float | None
    sector_concentration_pct: float | None
    geography_concentration_pct: float | None
    category_expense_ratio_pct: float | None
    score: float | None
    warnings: list[str]
    def as_dict(self): return asdict(self)

class ETFValuationEngine:
    def calculate(self, *, holdings=None, expense_ratio=None, nav_per_share=None, current_price=None,
                  premium_discount=None, tracking_difference=None, sector_concentration=None,
                  geography_concentration=None, category_expense_ratio=None):
        rows=[]
        for h in holdings or []:
            if isinstance(h,dict):
                ticker=h.get("ticker") or h.get("symbol") or h.get("holding") or "N/D"; name=h.get("name"); weight=h.get("weight_pct",h.get("weight",0))
            else:
                ticker=getattr(h,"ticker",getattr(h,"symbol","N/D")); name=getattr(h,"name",None); weight=getattr(h,"weight_pct",getattr(h,"weight",0))
            try: weight=float(weight)
            except (TypeError,ValueError): weight=0.0
            rows.append(ETFHolding(0,str(ticker),name,weight))
        rows=sorted(rows,key=lambda x:x.weight_pct,reverse=True)[:10]
        for i,r in enumerate(rows,1): r.rank=i
        top=[asdict(r) for r in rows]
        top_weight=round(sum(r.weight_pct for r in rows),4) if rows else None
        if premium_discount is None and nav_per_share and current_price:
            premium_discount=(float(current_price)/float(nav_per_share)-1)*100
        warnings=[]
        if not rows: warnings.append("ETF: composición no disponible")
        if expense_ratio is None: warnings.append("ETF: costo de administración (expense ratio) no disponible")
        if nav_per_share is None: warnings.append("ETF: NAV por participación no disponible")
        if tracking_difference is None: warnings.append("ETF: tracking difference no disponible")
        if sector_concentration is None: warnings.append("ETF: concentración sectorial no disponible")
        if geography_concentration is None: warnings.append("ETF: concentración geográfica no disponible")

        # Lower concentration is preferable. Top-10 <= 35% is excellent; >= 75% is very concentrated.
        concentration_score=None
        if top_weight is not None:
            concentration_score=max(0.0,min(100.0,100.0-(top_weight-35.0)*100.0/40.0)) if top_weight>35 else 100.0
        diversification_score=None
        if concentration_score is not None and sector_concentration is not None and geography_concentration is not None:
            sector=max(0.0,min(100.0,float(sector_concentration))); geo=max(0.0,min(100.0,float(geography_concentration)))
            diversification_score=round((concentration_score+(100-sector)+(100-geo))/3,2)

        expense_score=None
        if expense_ratio is not None:
            er=float(expense_ratio); expense_score=100.0 if er<=0.10 else max(0.0,min(100.0,100.0-(er-0.10)*100.0/1.00))
            if category_expense_ratio is not None:
                cat=float(category_expense_ratio)
                if cat>0: expense_score=max(0.0,min(100.0,70.0+(cat-er)/cat*30.0))
        tracking_score=None
        if tracking_difference is not None:
            td=abs(float(tracking_difference)); tracking_score=max(0.0,min(100.0,100.0-td*100.0))
        nav_score=None
        if premium_discount is not None:
            nav_score=max(0.0,min(100.0,100.0-abs(float(premium_discount))*20.0))
        components=[x for x in (diversification_score,expense_score,tracking_score,nav_score) if x is not None]
        quality_score=round(sum(components)/len(components),2) if components else None
        return ETFValuation("ETF_NAV_TRACKING",expense_ratio,top,top_weight,concentration_score,diversification_score,expense_score,tracking_score,nav_score,quality_score,nav_per_share,premium_discount,tracking_difference,sector_concentration,geography_concentration,category_expense_ratio,quality_score,warnings)
