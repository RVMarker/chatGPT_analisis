"""V12.23 consensus gate between provider data and BUY/SELL/HOLD decisions."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
from investment_analyzer.providers.provider_consensus import ProviderConsensus

@dataclass(slots=True)
class DecisionGateResult:
    status:str; decision_allowed:bool; coverage_pct:float; confidence_pct:float
    blocked_fields:list[str]; consensus:dict[str,dict[str,Any]]
    accepted_inputs:dict[str,Any]; warnings:list[str]
    def as_dict(self): return asdict(self)

class ConsensusDecisionGate:
    def __init__(self, consensus=None): self.consensus=consensus or ProviderConsensus()
    def evaluate(self, observations, *, critical_fields, minimum_coverage=.70, minimum_confidence=.60):
        results=self.consensus.evaluate_batch(observations,critical_fields=critical_fields); critical=set(critical_fields)
        available=sum(1 for f in critical if results.get(f) and results[f].accepted_value is not None)
        coverage=available/len(critical) if critical else 1.0
        scores=[results[f].quality_score for f in critical if f in results and results[f].status!="MISSING"]
        confidence=(sum(scores)/len(scores)/100) if scores else 0.0
        blocked=[f for f in critical if f not in results or not results[f].vote_allowed]
        allowed=coverage>=minimum_coverage and confidence>=minimum_confidence
        warnings=[]
        if blocked: warnings.append("Datos críticos bloqueados por consenso: "+", ".join(sorted(blocked)))
        if coverage<minimum_coverage: warnings.append(f"Cobertura decisoria insuficiente: {coverage:.1%}")
        if confidence<minimum_confidence: warnings.append(f"Confianza de datos insuficiente: {confidence:.1%}")
        return DecisionGateResult("PASS" if allowed else "BLOCK",allowed,coverage*100,confidence*100,blocked,{k:v.as_dict() for k,v in results.items()},self.consensus.decision_inputs(results),warnings)
    @staticmethod
    def protect_score(score, gate):
        if gate.decision_allowed:return max(0,min(100,float(score)))
        factor=max(0,min(1,gate.coverage_pct/100))*max(0,min(1,gate.confidence_pct/100))
        return round(50+(float(score)-50)*factor,2)
    @staticmethod
    def protect_verdict(verdict, gate, *, neutral="MANTENER"):
        return verdict if gate.decision_allowed else neutral
