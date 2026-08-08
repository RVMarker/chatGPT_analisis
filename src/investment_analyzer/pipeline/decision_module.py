"""Pipeline adapter for V11/V12 DecisionEngine with provenance-aware confidence."""
from __future__ import annotations
from investment_analyzer.analysis.decision.decision_engine import DecisionEngine

class DecisionModule:
    def __init__(self, engine: DecisionEngine | None = None): self.engine = engine or DecisionEngine()
    @staticmethod
    def _score(value, default=None):
        if isinstance(value, dict):
            if value.get("available") is False: return None
            for key in ("score", "total_score", "normalized_score", "rating"):
                if key in value: value=value[key]; break
        if value is None:return default
        try:return max(0.0,min(100.0,float(value)))
        except(TypeError,ValueError):return default
    @staticmethod
    def _technical_quality(context):
        result=getattr(context,"technical_result",{}) or {}
        if hasattr(result,"metadata"): metadata=result.metadata or {}; available=bool(metadata.get("available",True)); req=metadata.get("requirements",{}) or {}
        elif isinstance(result,dict): available=bool(result.get("available",False)); req=result.get("requirements",{}) or {}
        else:return 0.0
        if not available:return 0.0
        return 50.0 if not req else round(100.0*sum(bool(v) for v in req.values())/len(req),2)
    @staticmethod
    def _collect_strengths(context):
        out=[]
        for name, label in (("technical","Technical"),("fundamentals","Fundamental")):
            score=DecisionModule._score(getattr(context,name,{}) or {})
            if score is not None and score>=70:out.append(f"{label} score favorable ({score:.1f}/100)")
        return out
    @staticmethod
    def _collect_red_flags(context):
        technical=getattr(context,"technical",{}) or {}
        return [str(x) for x in technical.get("warnings",[]) or []] if isinstance(technical,dict) else []
    @staticmethod
    def _valuation_quality(context):
        valuation=getattr(context,"valuation",{}) or {}
        q=valuation.get("valuation_quality") if isinstance(valuation,dict) else None
        return str(q).upper() if q is not None else None
    @staticmethod
    def _provider_confidence(context):
        validation=(getattr(context,"metadata",{}) or {}).get("provider_validation",{}) or {}
        if not validation:return 80.0,80.0
        values=[float(v.get("confidence",0)) for v in validation.values() if v.get("status") != "MISSING"]
        conflicts=[v for v in validation.values() if v.get("status")=="CONFLICT"]
        score=round(sum(values)/len(values),2) if values else 0.0
        if conflicts: score=min(score,60.0)
        consistency=0.0 if conflicts else score
        return score,consistency
    def run(self, context):
        fundamental=self._score(context.fundamentals); valuation=self._score(context.valuation); risk=self._score(context.risk)
        technical=self._score(context.technical); sentiment=self._score(context.sentiment); smart_money=self._score(context.metadata.get("smart_money"))
        provider_data=context.metadata.get("data_providers",{}) or {}
        provider_values=[provider_data.get("price"),provider_data.get("financials")]
        present=[x for x in provider_values if x]
        completeness=round(100.0*len(present)/len(provider_values),2) if provider_values else 0.0
        provider_quality=round(100.0*sum(x=="yahoo" for x in present)/len(present),2) if present else 0.0
        provenance_quality,consistency=self._provider_confidence(context)
        provider_quality=min(provider_quality,provenance_quality) if present else provenance_quality
        technical_quality=self._technical_quality(context)
        freshness=100.0 if provider_data.get("history") else 0.0
        valuation_quality=self._valuation_quality(context)
        validation=(context.metadata.get("provider_validation",{}) or {})
        blocked=[k for k,v in validation.items() if v.get("vote_allowed") is False and v.get("status") != "MISSING"]
        result=self.engine.evaluate(
            strategic_scores={"fundamental":fundamental,"valuation":valuation,"risk":risk},
            tactical_scores={"technical":technical,"sentiment":sentiment,"smart_money":smart_money},
            confidence_inputs={"provider_quality":provider_quality,"freshness":freshness,"consistency":consistency,"completeness":completeness,"technical_data_quality":technical_quality,"valuation_quality":valuation_quality},
            strengths=self._collect_strengths(context),
            red_flags=self._collect_red_flags(context)+(["Campos bloqueados por conflicto: "+", ".join(blocked)] if blocked else []),
            contextual={"comparables":self._score(context.comparables),"macro":self._score(context.macro)},
        )
        result.missing_factors.extend([f"{x}: bloqueado por conflicto de fuentes" for x in blocked])
        result.base_confidence=min(result.base_confidence,provenance_quality)
        result.confidence=min(result.confidence,provenance_quality)
        context.decision=result
        return result
