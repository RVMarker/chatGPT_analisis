"""Pipeline adapter for V12 DecisionEngine with evidence-based scoring."""
from __future__ import annotations
from investment_analyzer.analysis.decision.confidence_engine import ConfidenceEngine
from investment_analyzer.analysis.decision.decision_engine import DecisionEngine
from investment_analyzer.analysis.decision.score_builder import build_scores

class DecisionModule:
    def __init__(self, engine=None, confidence_engine=None):
        self.engine=engine or DecisionEngine(); self.confidence_engine=confidence_engine or ConfidenceEngine()

    @staticmethod
    def _score(value, default=None):
        if isinstance(value,dict):
            if value.get("available") is False:return None
            for key in ("score","total_score","normalized_score","rating"):
                if key in value:value=value[key];break
        if value is None:return default
        try:return max(0.0,min(100.0,float(value)))
        except(TypeError,ValueError):return default

    @staticmethod
    def _technical_quality(context):
        result=getattr(context,"technical_result",{}) or {}
        if hasattr(result,"metadata"):
            metadata=result.metadata or {}; available=bool(metadata.get("available",True)); req=metadata.get("requirements",{}) or {}
        elif isinstance(result,dict): available=bool(result.get("available",False)); req=result.get("requirements",{}) or {}
        else:return 0.0
        if not available:return 0.0
        return 50.0 if not req else round(100.0*sum(bool(v) for v in req.values())/len(req),2)

    @staticmethod
    def _collect_strengths(context):
        out=[]
        for name,label in (("technical","Technical"),("fundamentals","Fundamental"),("valuation","Valuation"),("risk","Risk")):
            score=DecisionModule._score(getattr(context,name,{}) or {})
            if score is not None and score>=70:out.append(f"{label} score favorable ({score:.1f}/100)")
        return out

    @staticmethod
    def _collect_red_flags(context):
        technical=getattr(context,"technical",{}) or {}
        return [str(x) for x in technical.get("warnings",[]) or []] if isinstance(technical,dict) else []

    @staticmethod
    def _valuation_quality(context):
        valuation=getattr(context,"valuation",{}) or {}; q=valuation.get("valuation_quality") if isinstance(valuation,dict) else None
        return str(q).upper() if q is not None else None

    def run(self, context):
        metadata=getattr(context,"metadata",{}) or {}; validation=metadata.get("provider_validation",{}) or {}
        required_fields=list(validation.keys())
        confidence_result=self.confidence_engine.evaluate(required_fields,validation,base_quality=metadata.get("data_quality_score",100.0)) if required_fields else None
        evidence_confidence=confidence_result.confidence if confidence_result else 80.0; evidence_coverage=confidence_result.coverage if confidence_result else 100.0
        blocked=list(confidence_result.blocked) if confidence_result else []; missing=list(confidence_result.missing) if confidence_result else []
        provider_data=metadata.get("data_providers",{}) or {}; present=[x for x in (provider_data.get("price"),provider_data.get("financials")) if x]
        completeness=round(100.0*len(present)/2,2); provider_quality=round(100.0*sum(x=="yahoo" for x in present)/len(present),2) if present else 0.0
        technical_quality=self._technical_quality(context); freshness=100.0 if provider_data.get("history") else 0.0; valuation_quality=self._valuation_quality(context)
        scores=build_scores(context)
        result=self.engine.evaluate(strategic_scores=scores["strategic"],tactical_scores=scores["tactical"],confidence_inputs={"provider_quality":provider_quality,"freshness":freshness,"consistency":evidence_confidence,"completeness":completeness,"technical_data_quality":technical_quality,"valuation_quality":valuation_quality},strengths=self._collect_strengths(context),red_flags=self._collect_red_flags(context),contextual=scores["contextual"])
        result.data_coverage=evidence_coverage; result.confidence=evidence_confidence; result.base_confidence=evidence_confidence
        result.missing_factors.extend([f"{x}: sin evidencia utilizable" for x in missing]); result.missing_factors.extend([f"{x}: bloqueado por conflicto de fuentes" for x in blocked])
        if confidence_result:result.red_flags.append(f"Calidad evidencia: {confidence_result.data_quality:.1f}% | Cobertura utilizable: {confidence_result.coverage:.1f}%")
        result.red_flags=list(dict.fromkeys(result.red_flags)); context.decision=result; metadata["decision_scores"]=scores; metadata["confidence_result"]={"coverage":evidence_coverage,"data_quality":confidence_result.data_quality if confidence_result else 80.0,"confidence":evidence_confidence,"blocked":blocked,"missing":missing}; return result
