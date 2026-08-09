"""V12.45 end-to-end multi-asset investment pipeline with enriched ETF analysis."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
from investment_analyzer.providers.asset_classifier import AssetClassifier
from investment_analyzer.providers.instrument_identity import InstrumentIdentityRegistry
from investment_analyzer.providers.provider_consensus import ProviderConsensus
from investment_analyzer.providers.data_router import DataAcquisitionRouter
from investment_analyzer.providers.acquisition_engine import MultiProviderAcquisitionEngine
from investment_analyzer.analysis.etf_analyzer import ETFAnalyzer
from investment_analyzer.analysis.etf_scoring import ETFDecisionScorer
from investment_analyzer.analysis.decision_integration import SpecializedDecisionIntegrator

@dataclass(slots=True)
class PipelineResult:
    identity:dict[str,Any]; classification:dict[str,Any]; route:dict[str,Any]; acquisition:dict[str,Any]; specialized_analysis:dict[str,Any]; consensus:dict[str,dict[str,Any]]; analysis:dict[str,Any]; decision:dict[str,Any]; quality:dict[str,Any]; warnings:list[str]
    def as_dict(self): return asdict(self)

class InvestmentPipeline:
    def __init__(self,classifier=None,identity_registry=None,consensus=None,data_router=None,acquisition=None,etf_analyzer=None,etf_scorer=None,decision_integrator=None):
        self.classifier=classifier or AssetClassifier(); self.identity=identity_registry or InstrumentIdentityRegistry(); self.consensus=consensus or ProviderConsensus(); self.router=data_router or DataAcquisitionRouter(); self.acquisition=acquisition or MultiProviderAcquisitionEngine(self.router); self.etf_analyzer=etf_analyzer or ETFAnalyzer(); self.etf_scorer=etf_scorer or ETFDecisionScorer(); self.decision_integrator=decision_integrator or SpecializedDecisionIntegrator()
    @staticmethod
    def _decision(score,coverage,confidence):
        if coverage<60 or confidence<50:return "MANTENER"
        if score>=80:return "COMPRAR"
        if score>=65:return "ACUMULAR"
        if score>=45:return "MANTENER"
        if score>=30:return "REDUCIR"
        return "VENDER"
    def run(self,*,symbol,asset_type=None,isin=None,country=None,exchange=None,currency=None,provider_symbols=None,aliases=(),provider_metadata=None,consensus_data=None,analysis=None,strategic_score=None,strategic_coverage=0,tactical_score=None,tactical_coverage=0,data_quality=100.0,fetchers=None):
        md=provider_metadata or {}; classification=self.classifier.classify(symbol,provider_asset_type=asset_type,quote_type=md.get("quote_type"),description=md.get("description"),metadata=md); final_asset=classification.asset_type if asset_type is None else self.identity.normalize_asset_type(asset_type); route=self.router.plan(final_asset,symbol); ident=self.identity.register(asset_type=final_asset,symbol=symbol,isin=isin,country=country,exchange=exchange,currency=currency,provider_symbols=provider_symbols,aliases=aliases,metadata=md); acquisition=self.acquisition.acquire(symbol=symbol,asset_type=final_asset,fetchers=fetchers or {}); specialized={}; specialized_warnings=[]
        if final_asset=="ETF":
            enriched=acquisition.enriched or {}; canonical={k:enriched.get(k) for k in ("price","expense_ratio","benchmark","aum","holdings","tracking_difference","tracking_error")}; canonical["price"]=canonical.get("price") or (acquisition.fields.get("price") or [{}])[0].get("value"); etf=self.etf_analyzer.analyze(symbol,canonical); etf_dict=etf.as_dict(); score=self.etf_scorer.score(etf_dict,data_quality); etf_dict.update({"score":score.score,"score_components":score.components,"score_coverage":score.coverage,"score_warnings":score.warnings}); specialized={"etf":etf_dict}; specialized_warnings=(etf.warnings or [])+(score.warnings or [])
        consensus_input=consensus_data or {}
        if not consensus_input: consensus_input={field:[(x["provider"],x["value"]) for x in values] for field,values in acquisition.fields.items()}
        consensus=self.consensus.evaluate_batch(consensus_input,critical_fields=route["required_fields"]); blocked=[f for f,r in consensus.items() if not r.vote_allowed]; missing=acquisition.missing_required; cq=sum(r.quality_score for r in consensus.values())/len(consensus) if consensus else 0.0; completeness=100.0*(1-len(missing)/len(route["required_fields"])) if route["required_fields"] else 100.0; quality=min(float(data_quality),cq,completeness) if consensus else min(float(data_quality),completeness); warnings=[]
        if classification.confidence<70:warnings.append("Clasificación de activo con confianza inferior a 70%")
        if blocked:warnings.append("Datos críticos bloqueados por falta de consenso: "+", ".join(blocked))
        if missing:warnings.append("Datos requeridos ausentes: "+", ".join(missing))
        warnings.extend(specialized_warnings); strategic_conf=quality*(float(strategic_coverage)/100); tactical_conf=quality*(float(tactical_coverage)/100); decision={"strategic":{"score":strategic_score,"coverage":strategic_coverage,"confidence":round(strategic_conf,2),"verdict":self._decision(float(strategic_score if strategic_score is not None else 50),float(strategic_coverage),strategic_conf)},"tactical":{"score":tactical_score,"coverage":tactical_coverage,"confidence":round(tactical_conf,2),"verdict":self._decision(float(tactical_score if tactical_score is not None else 50),float(tactical_coverage),tactical_conf)}}
        if final_asset=="ETF" and "etf" in specialized: decision["strategic"]=self.decision_integrator.integrate(asset_type="ETF",strategic=decision["strategic"],specialized=specialized)
        return PipelineResult(ident.as_dict(),classification.as_dict(),route,acquisition.as_dict(),specialized,{k:r.as_dict() for k,r in consensus.items()},analysis or {},decision,{"data_quality":round(quality,2),"consensus_quality":round(cq,2),"completeness":round(completeness,2),"blocked_fields":blocked,"missing_required":missing},warnings)
