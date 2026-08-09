"""V12.34 provider health, fallback and audit trail."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

@dataclass(slots=True)
class ProviderAttempt:
    provider:str
    success:bool
    latency_ms:float
    error_type:str|None=None
    error_message:str|None=None
    fallback_from:str|None=None
    timestamp:str=""
    def as_dict(self): return asdict(self)

class ProviderHealthManager:
    def __init__(self): self.history=[]; self.stats={}
    def record(self,provider,success,latency_ms=0.0,error=None,fallback_from=None):
        item=ProviderAttempt(provider,bool(success),max(0.0,float(latency_ms)),type(error).__name__ if error else None,str(error) if error else None,fallback_from,datetime.now(timezone.utc).isoformat())
        self.history.append(item); s=self.stats.setdefault(provider,{"attempts":0,"successes":0,"failures":0,"total_latency_ms":0.0}); s["attempts"]+=1; s["successes"]+=int(bool(success)); s["failures"]+=int(not success); s["total_latency_ms"]+=item.latency_ms
        return item
    def health(self,provider):
        s=self.stats.get(provider,{"attempts":0,"successes":0,"failures":0,"total_latency_ms":0.0}); a=s["attempts"]
        return {"provider":provider,"attempts":a,"success_rate":round(100*s["successes"]/a,2) if a else 0.0,"avg_latency_ms":round(s["total_latency_ms"]/a,2) if a else 0.0}
    def fetch_with_fallback(self,providers,fetcher):
        attempts=[]
        for i,provider in enumerate(providers):
            try:
                result=fetcher(provider); self.record(provider,True,getattr(result,"latency_ms",0.0),fallback_from=providers[i-1] if i else None); return {"provider":provider,"result":result,"attempts":[x.as_dict() for x in attempts]}
            except Exception as exc:
                item=self.record(provider,False,error=exc,fallback_from=providers[i-1] if i else None); attempts.append(item)
        raise RuntimeError("Todos los proveedores fallaron: "+", ".join(providers))
    def audit(self): return [x.as_dict() for x in self.history]
