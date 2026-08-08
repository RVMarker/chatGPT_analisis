"""Provider consensus gate for investment-decision inputs."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Iterable

@dataclass(slots=True)
class ConsensusResult:
    field:str; status:str; accepted_value:Any; accepted_provider:str|None
    providers:list[str]; values:dict[str,Any]; dispersion_pct:float|None
    vote_allowed:bool; quality_score:float; reason:str
    def as_dict(self): return asdict(self)

class ProviderConsensus:
    DEFAULT_TOLERANCE={"price":.02,"market_cap":.05,"revenue":.05,"ebitda":.07,"eps":.10,"ffo":.10,"affo":.10,"net_debt":.10,"shares_outstanding":.03,"dividends_paid":.05,"ytm":.01,"coupon":.005,"volume":.15}
    def __init__(self,tolerances=None): self.tolerances={**self.DEFAULT_TOLERANCE,**(tolerances or {})}
    @staticmethod
    def _relative_dispersion(values):
        nums=[float(v) for v in values if isinstance(v,(int,float))]
        if len(nums)<2:return None
        mean=sum(nums)/len(nums)
        return None if mean==0 else (max(nums)-min(nums))/abs(mean)
    def evaluate(self,field:str,observations:Iterable[tuple[str,Any]],*,critical=True):
        obs=[(str(p),v) for p,v in observations if v is not None]
        if not obs:return ConsensusResult(field,"MISSING",None,None,[],{},None,False,0.0,"Sin datos de proveedor")
        values={p:v for p,v in obs}; dispersion=self._relative_dispersion([v for _,v in obs]); tol=self.tolerances.get(field,.05)
        if len(obs)==1:return ConsensusResult(field,"SINGLE_PROVIDER",obs[0][1],obs[0][0],[p for p,_ in obs],values,dispersion,not critical,65.0,"Un solo proveedor; no hay consenso independiente")
        if dispersion is None:
            same=len({str(v) for _,v in obs})==1
            return ConsensusResult(field,"CONSENSUS" if same else "CONFLICT",obs[0][1] if same else None,obs[0][0] if same else None,[p for p,_ in obs],values,dispersion,same,95.0 if same else 0.0,"Valores idénticos" if same else "Valores no numéricos en conflicto")
        ordered=sorted(obs,key=lambda x:float(x[1])); median=float(ordered[len(ordered)//2][1]); nearest=min(obs,key=lambda x:abs(float(x[1])-median)); allowed=dispersion<=tol
        score=max(0.0,min(100.0,100.0-(dispersion/tol)*20.0)) if allowed else 0.0
        return ConsensusResult(field,"CONSENSUS" if allowed else "CONFLICT",nearest[1] if allowed else None,nearest[0] if allowed else None,[p for p,_ in obs],values,dispersion,allowed,score,f"Dispersión {dispersion:.2%}; tolerancia {tol:.2%}")
    def evaluate_batch(self,data:dict[str,Iterable[tuple[str,Any]]],critical_fields=None):
        critical=set(critical_fields or data.keys())
        return {f:self.evaluate(f,o,critical=f in critical) for f,o in data.items()}
    @staticmethod
    def decision_inputs(results): return {f:r.accepted_value for f,r in results.items() if r.vote_allowed and r.accepted_value is not None}
