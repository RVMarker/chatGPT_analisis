"""Canonical instrument identity and provider ticker aliases."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Iterable

@dataclass(slots=True)
class InstrumentIdentity:
    canonical_id: str
    asset_type: str
    symbol: str
    country: str|None = None
    exchange: str|None = None
    currency: str|None = None
    isin: str|None = None
    provider_symbols: dict[str,str] = field(default_factory=dict)
    aliases: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    def as_dict(self): return asdict(self)

class InstrumentIdentityRegistry:
    ASSET_ALIASES={"EQUITY":"STOCK","STOCK":"STOCK","ETF":"ETF","REIT":"REIT","FIBRA":"FIBRA","CRYPTO":"CRYPTO","BOND":"BOND"}
    PROVIDER_ALIASES={
        "yahoo": {"MX": ".MX"},
        "fmp": {"MX": ""},
        "alphavantage": {"MX": ""},
        "twelvedata": {"MX": ""},
    }
    def __init__(self): self._items={}
    @classmethod
    def normalize_asset_type(cls,value):
        key=str(value or "").strip().upper().replace(" ","_")
        return cls.ASSET_ALIASES.get(key,key)
    @staticmethod
    def _norm_symbol(value): return str(value or "").strip().upper()
    @classmethod
    def canonical_id(cls,*,asset_type,symbol=None,isin=None,country=None):
        asset=cls.normalize_asset_type(asset_type); ident=isin or symbol or "UNKNOWN"
        if isin: return f"{asset}:ISIN:{cls._norm_symbol(isin)}"
        return f"{asset}:{cls._norm_symbol(country or 'GLOBAL')}:{cls._norm_symbol(ident)}"
    def register(self,*,asset_type,symbol,isin=None,country=None,exchange=None,currency=None,provider_symbols=None,aliases:Iterable[str]=(),metadata=None):
        asset=self.normalize_asset_type(asset_type); canonical=self.canonical_id(asset_type=asset,symbol=symbol,isin=isin,country=country)
        providers={str(k).lower():self._norm_symbol(v) for k,v in dict(provider_symbols or {}).items() if v}
        alias_list=list(dict.fromkeys(self._norm_symbol(x) for x in aliases if x))
        # Common Mexican notation: user-facing FMTY14.MX can map to provider-specific forms.
        raw=self._norm_symbol(symbol)
        if country and self._norm_symbol(country) in {"MX","MEX","MEXICO"}:
            bare=raw[:-3] if raw.endswith(".MX") else raw
            alias_list.extend([raw,bare,bare+".MX"])
            alias_list=list(dict.fromkeys(alias_list))
        item=InstrumentIdentity(canonical,asset,raw,country,exchange,currency,isin,providers,alias_list,dict(metadata or {})); self._items[canonical]=item; return item
    def resolve(self,*,canonical_id=None,symbol=None,provider=None,isin=None):
        if canonical_id and canonical_id in self._items:return self._items[canonical_id]
        needle=self._norm_symbol(isin or symbol)
        provider_key=str(provider or "").lower()
        for item in self._items.values():
            if item.isin and self._norm_symbol(item.isin)==needle:return item
            if item.symbol==needle or needle in item.aliases:return item
            if provider_key and self._norm_symbol(item.provider_symbols.get(provider_key,""))==needle:return item
        return None
    def provider_symbol(self,item:InstrumentIdentity,provider:str)->str:
        key=str(provider).lower(); explicit=item.provider_symbols.get(key)
        if explicit:return explicit
        symbol=item.symbol
        country=self._norm_symbol(item.country)
        if country in {"MX","MEX","MEXICO"}:
            bare=symbol[:-3] if symbol.endswith(".MX") else symbol
            return bare+".MX" if key=="yahoo" else bare
        return symbol
    def provider_symbols_all(self,item:InstrumentIdentity)->dict[str,str]:
        return {provider:self.provider_symbol(item,provider) for provider in ("yahoo","fmp","alphavantage","twelvedata","coingecko","binance")}
    def to_provider_request(self,item:InstrumentIdentity,provider:str)->dict:
        return {"canonical_id":item.canonical_id,"asset_type":item.asset_type,"symbol":self.provider_symbol(item,provider),"isin":item.isin}
