"""V12.32 end-to-end multi-asset investment pipeline."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
from investment_analyzer.providers.asset_classifier import AssetClassifier
from investment_analyzer.providers.instrument_identity import InstrumentIdentityRegistry
from investment_analyzer.providers.provider_consensus import ProviderConsensus
from investment_analyzer.providers.data_router import DataAcquisitionRouter

@dataclass(slots=True)
class PipelineResult:
    identity:dict[str,Any]; classification:dict[str,Any]; route:dict[str,Any]; consensus:dict[str,dict[str,Any]]; analysis:dict[str,Any]; decision:dict[str,Any]; quality:dict[str,Any]; warnings:list[str]
    def as_dict(self): return asdict(self)

class InvestmentPipeline:
    def __init__(self,classifier=None,identity_registry=None,consensus=None,data_router=None):
        self.classifier=classifier or AssetClassifier(); self.identity=identity_registry or InstrumentIdentityRegistry(); self.consensus=consensus or ProviderConsensus(); self.router=data_router or DataAcquisitionRouter()
    @staticmethod
    def _decision(score,coverage,confidence):
        if coverage<60 or confidence<50:return "MANTENER"
        if score>=80:return "COMPRAR"
        if score>=65:return "ACUMULAR"
        if score>=45:return "MANTENER"
        if score>=30:return "REDUCIR"
        return "VENDER"
    def run(self,*,symbol,asset_type=None,isin=None,country=None,exchange=None,currency=None,provider_symbols=None,aliases=(),provider_metadata=None,consensus_data=None,analysis=None,strategic_score=None,strategic_coverage=0,tactical_score=None,tactical_coverage=0,data_quality=100.0):
        md=provider_metadata or {}
        classification=self.classifier.classify(symbol,provider_asset_type=asset_type,quote_type=md.get("quote_type"),description=md.get("description"),metadata=md)
        final_asset=classification.asset_type if asset_type is None else self.identity.normalize_asset_type(asset_type)
        route=self.router.plan(final_asset,symbol)
        ident=self.identity.register(asset_type=final_asset,symbol=symbol,isin=isin,country=country,exchange=exchange,currency=currency,provider_symbols=provider_symbols,aliases=aliases,metadata=md)
        consensus=self.consensus.evaluate_batch(consensus_data or {},critical_fields=(consensus_data or {}).keys())
        blocked=[f for f,r in consensus.items() if not r.vote_allowed]; cq=sum(r.quality_score for r in consensus.values())/len(consensus) if consensus else 100.0; quality=min(float(data_quality),cq); warnings=[]
        if classification.confidence<70:warnings.append("Clasificación de activo con confianza inferior a 70%")
        if blocked:warnings.append("Datos críticos bloqueados por falta de consenso: "+", ".join(blocked))
        strategic_conf=quality*(float(strategic_coverage)/100); tactical_conf=quality*(float(tactical_coverage)/100)
        decision={"strategic":{"score":strategic_score,"coverage":strategic_coverage,"confidence":round(strategic_conf,2),"verdict":self._decision(float(strategic_score if strategic_score is not None else 50),float(strategic_coverage),strategic_conf)},"tactical":{"score":tactical_score,"coverage":tactical_coverage,"confidence":round(tactical_conf,2),"verdict":self._decision(float(tactical_score if tactical_score is not None else 50),float(tactical_coverage),tactical_conf)}}
        return PipelineResult(ident.as_dict(),classification.as_dict(),route,{k:r.as_dict() for k,r in consensus.items()},analysis or {},decision,{"data_quality":round(quality,2),"consensus_quality":round(cq,2),"blocked_fields":blocked},warnings)
