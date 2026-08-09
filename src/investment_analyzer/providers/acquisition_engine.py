"""V12.78 acquisition using canonical instrument identity and provider aliases."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Callable
from investment_analyzer.providers.data_router import DataAcquisitionRouter
from investment_analyzer.providers.normalizer import ProviderNormalizer
from investment_analyzer.providers.provider_health import ProviderHealthManager
from investment_analyzer.providers.instrument_identity import InstrumentIdentityRegistry, InstrumentIdentity
from investment_analyzer.analysis.etf_enrichment import ETFEnricher
from investment_analyzer.analysis.reit_fibra_enrichment import REITFibraEnricher

@dataclass(slots=True)
class AcquisitionResult:
    symbol:str; asset_type:str; fields:dict[str,Any]; provider_used:dict[str,str]; provider_errors:list[dict[str,Any]]; missing_required:list[str]; route:dict[str,Any]; enriched:dict[str,Any]|None=None
    def as_dict(self): return asdict(self)

class MultiProviderAcquisitionEngine:
    def __init__(self,router=None,normalizer=None,health=None,etf_enricher=None,reit_fibra_enricher=None,identity_registry=None):
        self.router=router or DataAcquisitionRouter(); self.normalizer=normalizer or ProviderNormalizer(); self.health=health or ProviderHealthManager(); self.etf_enricher=etf_enricher or ETFEnricher(); self.reit_fibra_enricher=reit_fibra_enricher or REITFibraEnricher(); self.identity=identity_registry or InstrumentIdentityRegistry()
    def acquire(self,*,symbol,asset_type,fetchers:dict[str,Callable[[str],Any]],identity:InstrumentIdentity|None=None):
        route=self.router.route(asset_type); raw={}; used={}; errors=[]; provider_payloads={}; identity=identity or self.identity.register(asset_type=asset_type,symbol=symbol)
        for field in route.required_fields+route.optional_fields:
            for provider in route.providers:
                fetcher=fetchers.get(provider)
                if not fetcher: continue
                provider_symbol=self.identity.provider_symbol(identity,provider)
                try:
                    payload=provider_payloads.get(provider)
                    if payload is None: payload=fetcher(provider_symbol) or {}; provider_payloads[provider]=payload
                    normalized=self.normalizer.normalize(payload,provider); item=normalized.get(field)
                    if item and not item.missing: raw.setdefault(field,[]).append(item); used[field]=provider; break
                except Exception as exc:
                    attempt=self.health.record(provider,False,error=exc); errors.append(attempt.as_dict())
        enriched=None; asset=asset_type.upper()
        if asset=="ETF":
            enriched=self.etf_enricher.enrich(provider_payloads).as_dict(); keys=("expense_ratio","benchmark","aum","holdings","tracking_difference","tracking_error")
        elif asset in {"REIT","FIBRA"}:
            enriched=self.reit_fibra_enricher.enrich(provider_payloads); keys=tuple(self.reit_fibra_enricher.ALIASES)
        else: keys=()
        if enriched:
            for key in keys:
                if enriched.get(key) is not None and enriched.get(key)!=[]: used.setdefault(key,enriched.get("source_map",{}).get(key,"enriched"))
        missing=[f for f in route.required_fields if f not in raw]
        fields={k:[asdict(v) for v in vals] for k,vals in raw.items()}
        return AcquisitionResult(identity.symbol,route.asset_type,fields,used,errors,missing,{**route.as_dict()},enriched)
