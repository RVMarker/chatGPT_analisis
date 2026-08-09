"""V12.45 acquisition with multi-provider ETF enrichment."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Callable
from investment_analyzer.providers.data_router import DataAcquisitionRouter
from investment_analyzer.providers.normalizer import ProviderNormalizer
from investment_analyzer.providers.provider_health import ProviderHealthManager
from investment_analyzer.analysis.etf_enrichment import ETFEnricher

@dataclass(slots=True)
class AcquisitionResult:
    symbol:str; asset_type:str; fields:dict[str,Any]; provider_used:dict[str,str]; provider_errors:list[dict[str,Any]]; missing_required:list[str]; route:dict[str,Any]; enriched:dict[str,Any]|None=None
    def as_dict(self): return asdict(self)

class MultiProviderAcquisitionEngine:
    def __init__(self,router=None,normalizer=None,health=None,etf_enricher=None):
        self.router=router or DataAcquisitionRouter(); self.normalizer=normalizer or ProviderNormalizer(); self.health=health or ProviderHealthManager(); self.etf_enricher=etf_enricher or ETFEnricher()
    def acquire(self,*,symbol,asset_type,fetchers:dict[str,Callable[[str],Any]]):
        route=self.router.route(asset_type); raw={}; used={}; errors=[]; provider_payloads={}
        for field in route.required_fields+route.optional_fields:
            for provider in route.providers:
                fetcher=fetchers.get(provider)
                if not fetcher: continue
                try:
                    payload=provider_payloads.get(provider)
                    if payload is None: payload=fetcher(symbol) or {}; provider_payloads[provider]=payload
                    normalized=self.normalizer.normalize(payload,provider); item=normalized.get(field)
                    if item and not item.missing: raw.setdefault(field,[]).append(item); used[field]=provider; break
                except Exception as exc:
                    attempt=self.health.record(provider,False,error=exc); errors.append(attempt.as_dict())
        enriched=None
        if asset_type.upper()=="ETF":
            enriched=self.etf_enricher.enrich(provider_payloads).as_dict()
            for key in ("expense_ratio","benchmark","aum","holdings","tracking_difference","tracking_error"):
                if enriched.get(key) is not None and enriched.get(key)!=[]: used.setdefault(key,enriched.get("source_map",{}).get(key,"enriched"))
        missing=[f for f in route.required_fields if f not in raw]
        fields={k:[asdict(v) for v in vals] for k,vals in raw.items()}
        return AcquisitionResult(symbol,route.asset_type,fields,used,errors,missing,{**route.as_dict()},enriched)
