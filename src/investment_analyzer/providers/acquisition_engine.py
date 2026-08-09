"""V12.35 acquisition: route -> fallback -> normalized canonical fields."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Callable
from investment_analyzer.providers.data_router import DataAcquisitionRouter
from investment_analyzer.providers.normalizer import ProviderNormalizer
from investment_analyzer.providers.provider_health import ProviderHealthManager

@dataclass(slots=True)
class AcquisitionResult:
    symbol:str
    asset_type:str
    fields:dict[str,Any]
    provider_used:dict[str,str]
    provider_errors:list[dict[str,Any]]
    missing_required:list[str]
    route:dict[str,Any]
    def as_dict(self): return asdict(self)

class MultiProviderAcquisitionEngine:
    def __init__(self,router=None,normalizer=None,health=None):
        self.router=router or DataAcquisitionRouter(); self.normalizer=normalizer or ProviderNormalizer(); self.health=health or ProviderHealthManager()
    def acquire(self,*,symbol,asset_type,fetchers:dict[str,Callable[[str],Any]]):
        route=self.router.route(asset_type); raw={}; used={}; errors=[]
        for field in route.required_fields+route.optional_fields:
            for provider in route.providers:
                fetcher=fetchers.get(provider)
                if not fetcher: continue
                try:
                    payload=fetcher(symbol) or {}; normalized=self.normalizer.normalize(payload,provider); item=normalized.get(field)
                    if item and not item.missing:
                        raw.setdefault(field,[]).append(item); used[field]=provider; self.health.record(provider,True); break
                except Exception as exc:
                    attempt=self.health.record(provider,False,error=exc); errors.append(attempt.as_dict())
        missing=[f for f in route.required_fields if f not in raw]
        fields={k:[asdict(v) for v in vals] for k,vals in raw.items()}
        return AcquisitionResult(symbol,route.asset_type,fields,used,errors,missing,{**route.as_dict()})
