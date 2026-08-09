"""V12.80 transparent ETF strategic scoring with concentration risk."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from typing import Any

@dataclass(slots=True)
class ETFScore:
    score:float; components:dict[str,dict[str,float]]; coverage:float; warnings:list[str]
    def as_dict(self): return asdict(self)

class ETFDecisionScorer:
    WEIGHTS={"cost":25.0,"diversification":25.0,"tracking":20.0,"scale":15.0,"data_quality":15.0}
    def score(self,analysis:dict[str,Any],data_quality:float=100.0):
        warnings=[]; vals={}
        expense=analysis.get("expense_ratio")
        if expense is None: warnings.append("Expense ratio ausente: componente de costo no vota"); cost=None
        else:
            e=float(expense)*100 if float(expense)<=1 else float(expense); cost=max(0,min(100,100-e*1000))
        top10=analysis.get("top10_weight")
        diversification=None if top10 is None else max(0,min(100,100-float(top10)))
        if diversification is None: warnings.append("Concentración TOP 10 ausente: diversificación no vota")
        tracking=analysis.get("tracking_score")
        if tracking is None:
            td=analysis.get("tracking_difference"); te=analysis.get("tracking_error")
            tracking=50.0
            if td is not None: tracking=max(0,min(100,100-abs(float(td))*100))
            if te is not None: tracking=max(0,min(100,tracking-float(te)*50))
            if td is None and te is None: warnings.append("Tracking error/difference no disponible: score neutral")
        aum=analysis.get("aum")
        scale=None if aum is None else (min(100,(float(aum)/1_000_000_000)*50+50) if float(aum)>0 else 0)
        if scale is None: warnings.append("AUM ausente: escala no vota")
        vals={"cost":cost,"diversification":diversification,"tracking":max(0,min(100,float(tracking))),"scale":scale,"data_quality":max(0,min(100,float(data_quality)))}
        active=sum(self.WEIGHTS[k] for k,v in vals.items() if v is not None)
        score=sum(self.WEIGHTS[k]*v for k,v in vals.items() if v is not None)/active if active else 0
        components={k:{"score":round(v,2),"weight":self.WEIGHTS[k],"contribution":round(self.WEIGHTS[k]*v/active,2)} for k,v in vals.items() if v is not None}
        return ETFScore(round(score,2),components,round(active,2),warnings)
