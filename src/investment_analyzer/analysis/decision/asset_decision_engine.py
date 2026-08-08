"""V12.19 unified asset-aware decision engine."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Mapping

@dataclass(slots=True)
class AssetDecision:
    asset_type:str; strategic_score:float|None; tactical_score:float|None
    strategic_verdict:str; tactical_verdict:str; strategic_coverage:float
    tactical_coverage:float; confidence:float; strategic_breakdown:list[dict[str,Any]]
    tactical_breakdown:list[dict[str,Any]]; contextual:dict[str,Any]; warnings:list[str]
    def as_dict(self): return asdict(self)

class AssetDecisionEngine:
    ALIASES={"STOCK":"STOCK","EQUITY":"STOCK","ETF":"ETF","REIT":"REIT","FIBRA":"FIBRA","CRYPTO":"CRYPTO","BOND":"BOND"}
    WEIGHTS={
      "STOCK":{"strategic":{"fundamental":.35,"valuation":.35,"risk":.30},"tactical":{"technical":.60,"sentiment":.20,"smart_money":.20}},
      "ETF":{"strategic":{"quality":.35,"valuation":.25,"risk":.20,"benchmark":.20},"tactical":{"technical":.60,"sentiment":.20,"smart_money":.20}},
      "REIT":{"strategic":{"fundamental":.30,"valuation":.40,"risk":.30},"tactical":{"technical":.60,"sentiment":.20,"smart_money":.20}},
      "FIBRA":{"strategic":{"fundamental":.30,"valuation":.40,"risk":.30},"tactical":{"technical":.60,"sentiment":.20,"smart_money":.20}},
      "CRYPTO":{"strategic":{"tokenomics":.25,"network":.25,"valuation":.25,"risk":.25},"tactical":{"technical":.55,"sentiment":.25,"smart_money":.20}},
      "BOND":{"strategic":{"value":.35,"credit":.30,"rate_risk":.20,"real_yield":.15},"tactical":{"technical":.40,"rates":.40,"liquidity":.20}},
    }
    def normalize(self,asset_type):
        key=str(asset_type or "STOCK").strip().upper().replace(" ","_")
        if key not in self.ALIASES: raise ValueError(f"Clase de activo no soportada: {asset_type}")
        return self.ALIASES[key]
    @staticmethod
    def _score(v):
        if isinstance(v,Mapping): v=v.get("score",v.get("quality_score",v.get("total_score")))
        try: return max(0.,min(100.,float(v))) if v is not None else None
        except (TypeError,ValueError): return None
    @staticmethod
    def _weighted(scores,weights):
        rows=[]
        for name,w in weights.items():
            score=AssetDecisionEngine._score(scores.get(name)); rows.append({"name":name,"score":None if score is None else round(score,2),"weight":w,"available":score is not None})
        active=[r for r in rows if r["available"]]; coverage=round(100*len(active)/len(rows),2) if rows else 0.; total_w=sum(r["weight"] for r in active)
        total=round(sum(r["score"]*r["weight"]/total_w for r in active),2) if total_w else None
        for r in rows:
            r["effective_weight"]=round(r["weight"]/total_w,4) if r["available"] and total_w else 0.; r["contribution"]=round(r["score"]*r["effective_weight"],2) if r["available"] else 0.
        return total,coverage,rows
    @staticmethod
    def _verdict(score):
        if score is None:return "N/D"
        if score>=80:return "COMPRAR"
        if score>=70:return "ACUMULAR"
        if score>=50:return "MANTENER"
        if score>=35:return "REDUCIR"
        return "VENDER"
    def evaluate(self,asset_type,strategic_scores,tactical_scores,*,contextual=None,base_confidence=100.,data_quality=100.,warnings=None):
        asset=self.normalize(asset_type); cfg=self.WEIGHTS[asset]; ss,sc,sb=self._weighted(strategic_scores,cfg["strategic"]); ts,tc,tb=self._weighted(tactical_scores,cfg["tactical"])
        confidence=round(max(0,min(100,float(base_confidence)))*max(0,min(100,float(data_quality)))/100*min(sc,tc)/100,2)
        warn=list(warnings or [])
        for group,cov in (("estratégica",sc),("táctica",tc)):
            if cov<100: warn.append(f"Cobertura {group}: {cov:.1f}%; factores faltantes no fueron convertidos en 50.")
        return AssetDecision(asset,ss,ts,self._verdict(ss),self._verdict(ts),sc,tc,confidence,sb,tb,dict(contextual or {}),list(dict.fromkeys(warn)))
