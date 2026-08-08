"""Transparent V11 decision engine with an auditable decision trail."""
from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Mapping
from .decision_weights import STRATEGIC, TACTICAL, validate_weights

@dataclass(slots=True)
class ScoreComponent:
    name: str; score: float | None; weight: float; explanation: str = ""; available: bool = True; role: str = "VOTE"; evidence: list[str] = field(default_factory=list)
    @property
    def weighted(self): return (self.score or 0.0) * self.weight
    @property
    def contribution_pct(self): return self.weighted
    def as_dict(self): return {"name":self.name,"score":round(self.score,2) if self.score is not None else None,"weight":round(self.weight,4),"weighted_contribution":round(self.weighted,2),"contribution_pct":round(self.contribution_pct,2),"explanation":self.explanation,"available":self.available,"role":self.role,"evidence":list(self.evidence)}

@dataclass(slots=True)
class DecisionResult:
    strategic_score: float | None; tactical_score: float | None; strategic_decision: str; tactical_decision: str; confidence: float
    strategic_breakdown: list[ScoreComponent] = field(default_factory=list); tactical_breakdown: list[ScoreComponent] = field(default_factory=list)
    red_flags: list[str] = field(default_factory=list); strengths: list[str] = field(default_factory=list); contextual: dict[str,float] = field(default_factory=dict)
    data_coverage: float = 100.0; base_confidence: float = 100.0; strategic_coverage: float = 100.0; tactical_coverage: float = 100.0
    strategic_sufficient: bool = True; tactical_sufficient: bool = True; decision_trail: list[dict[str,object]] = field(default_factory=list)
    decisive_factors: list[str] = field(default_factory=list); contextual_factors: list[str] = field(default_factory=list); missing_factors: list[str] = field(default_factory=list)
    actionable: dict = field(default_factory=dict)
    def breakdown_dict(self): return {"strategic":[x.as_dict() for x in self.strategic_breakdown],"tactical":[x.as_dict() for x in self.tactical_breakdown]}

class DecisionEngine:
    BUY, ACCUMULATE, HOLD, REDUCE = 80.0,70.0,50.0,35.0; MIN_DECISION_COVERAGE = 50.0
    def __init__(self): validate_weights()
    @classmethod
    def _decision(cls,score):
        if score is None:return "N/D"
        if score>=cls.BUY:return "COMPRAR"
        if score>=cls.ACCUMULATE:return "ACUMULAR"
        if score>=cls.HOLD:return "MANTENER"
        if score>=cls.REDUCE:return "REDUCIR"
        return "VENDER"
    @staticmethod
    def _score(value,default=None):
        if value is None:return default
        try:return max(0.0,min(100.0,float(value)))
        except(TypeError,ValueError):return default
    @staticmethod
    def _normalize_weight(weight,total):return float(Decimal(str(weight))/Decimal(str(total)))
    def _weighted(self,data:Mapping[str,object],weights:Mapping[str,float]):
        items=[]
        for key,weight in weights.items():
            raw=data.get(key); available=raw is not None and not(isinstance(raw,Mapping) and raw.get("available") is False)
            score=self._score(raw.get("score")) if isinstance(raw,Mapping) and available else self._score(raw) if available else None
            items.append(ScoreComponent(key,score,weight,"Disponible" if available and score is not None else "NO DISPONIBLE — no participa en el promedio",available and score is not None,"VOTE"))
        available_items=[x for x in items if x.available]
        if not available_items:return None,items,["Ningún componente disponible; veredicto N/D"]
        total_weight=sum(x.weight for x in available_items)
        for x in available_items:x.weight=self._normalize_weight(x.weight,total_weight)
        return sum(x.weighted for x in available_items),items,[]
    @staticmethod
    def _coverage(items):return round(100.0*sum(x.available for x in items)/len(items),2) if items else 0.0
    def strategic(self,data):return self._weighted(data,STRATEGIC)
    def tactical(self,data):return self._weighted(data,TACTICAL)
    @staticmethod
    def _quality_score(value):
        if value is None:return 100.0
        if isinstance(value,(int,float)):return max(0.0,min(100.0,float(value)))
        return {"HIGH":100.0,"MEDIUM_HIGH":90.0,"MEDIUM":75.0,"LOW_MEDIUM":60.0,"LOW":50.0}.get(str(value).upper(),100.0)
    @staticmethod
    def confidence(provider_quality,freshness,consistency,completeness,technical_data_quality=100.0,coverage=100.0,valuation_quality=None):
        vals=[max(0,min(100,float(v))) for v in [provider_quality,freshness,consistency,completeness,technical_data_quality]]; q=DecisionEngine._quality_score(valuation_quality)
        base=vals[0]*.243+vals[1]*.162+vals[2]*.243+vals[3]*.162+vals[4]*.090+q*.100
        return round(base*max(0,min(100,float(coverage)))/100,2)
    @staticmethod
    def _trail(items,horizon):
        return [{"horizon":horizon,"factor":i.name,"role":"VOTE" if i.available else "MISSING","score":i.score,"weight":i.weight,"contribution":round(i.weighted,2),"effect":"positive" if i.available and i.score>=60 else "negative" if i.available and i.score<40 else "neutral" if i.available else "unknown"} for i in items]
    def evaluate(self,strategic_scores,tactical_scores,confidence_inputs,strengths=None,red_flags=None,contextual=None):
        st,si,sw=self.strategic(strategic_scores); tt,ti,tw=self.tactical(tactical_scores); sc,tc=self._coverage(si),self._coverage(ti); coverage=round((sc+tc)/2,2)
        vq=confidence_inputs.get("valuation_quality"); args=(confidence_inputs.get("provider_quality",80),confidence_inputs.get("freshness",80),confidence_inputs.get("consistency",80),confidence_inputs.get("completeness",80),confidence_inputs.get("technical_data_quality",100)); base=self.confidence(*args,100,vq); confidence=self.confidence(*args,coverage,vq)
        context={}; contextual_factors=[]
        for key,value in(contextual or {}).items():
            score=self._score(value)
            if score is not None:context[key]=score; contextual_factors.append(f"{key}: contexto; no vota directamente")
        strategic_sufficient=st is not None and sc>=self.MIN_DECISION_COVERAGE; tactical_sufficient=tt is not None and tc>=self.MIN_DECISION_COVERAGE
        flags=list(red_flags or [])+sw+tw
        for item in si+ti:
            if not item.available:flags.append(f"{item.name}: NO DISPONIBLE; excluido del promedio ponderado")
        if vq is not None and str(vq).upper()!="HIGH":flags.append(f"Calidad de valoración {str(vq).upper()}: reduce confianza, pero no altera score/veredicto")
        if coverage<100:flags.append(f"Cobertura de señales decisorias: {coverage:.1f}%")
        trail=self._trail(si,"estratégico")+self._trail(ti,"táctico"); decisive=[]; missing=[]
        for item in si+ti:
            if item.available:
                if item.score<40:decisive.append(f"{item.name} presiona a la baja ({item.score:.1f}/100)")
                elif item.score>=70:decisive.append(f"{item.name} apoya la tesis ({item.score:.1f}/100)")
            else:missing.append(f"{item.name}: sin dato decisorio")
        if vq is not None and str(vq).upper()!="HIGH":missing.append(f"Calidad valoración: {str(vq).upper()}")
        return DecisionResult(round(st,2) if st is not None else None,round(tt,2) if tt is not None else None,self._decision(st),self._decision(tt),confidence,si,ti,list(dict.fromkeys(flags)),list(strengths or []),context,coverage,base,sc,tc,strategic_sufficient,tactical_sufficient,trail,decisive,contextual_factors,missing,{})
    @staticmethod
    def print_summary(result):
        print("="*80);print("DECISION ENGINE V11");print("="*80);print(f"Estratégico (años): {result.strategic_decision} | {result.strategic_score:.2f}/100");print(f"Táctico (semanas):  {result.tactical_decision} | {result.tactical_score:.2f}/100");print(f"Confianza:          {result.confidence:.1f}%");print(f"Cobertura señales:  {result.data_coverage:.1f}%")
