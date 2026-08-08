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
    def __init__(self): self._items={}
    @classmethod
    def normalize_asset_type(cls,value):
        key=str(value or "").strip().upper().replace(" ","_")
        return cls.ASSET_ALIASES.get(key,key)
    @staticmethod
    def canonical_id(*,asset_type,symbol=None,isin=None,country=None):
        asset=str(asset_type).upper(); ident=isin or symbol or "UNKNOWN"
        if isin: return f"{asset}:ISIN:{str(isin).upper()}"
        return f"{asset}:{str(country or 'GLOBAL').upper()}:{str(ident).upper()}"
    def register(self, *, asset_type, symbol, isin=None, country=None, exchange=None, currency=None, provider_symbols=None, aliases:Iterable[str]=(), metadata=None):
        asset=self.normalize_asset_type(asset_type); cid=self.canonical_id(asset_type=asset,symbol=symbol,isin=isin,country=country)
        item=InstrumentIdentity(cid,asset,str(symbol).upper(),country,exchange,currency,isin,dict(provider_symbols or {}),list(dict.fromkeys(str(x).upper() for x in aliases)),dict(metadata or {})); self._items[cid]=item; return item
    def resolve(self, *, canonical_id=None, symbol=None, provider=None, isin=None):
        if canonical_id and canonical_id in self._items: return self._items[canonical_id]
        needle=str(isin or symbol or "").upper()
        for item in self._items.values():
            if item.isin and item.isin.upper()==needle: return item
            if item.symbol.upper()==needle or needle in item.aliases: return item
            if provider and item.provider_symbols.get(provider,"").upper()==needle: return item
        return None
    def provider_symbol(self,item:InstrumentIdentity,provider:str)->str:
        return item.provider_symbols.get(provider,item.symbol)
    def to_provider_request(self,item:InstrumentIdentity,provider:str)->dict:
        return {"canonical_id":item.canonical_id,"asset_type":item.asset_type,"symbol":self.provider_symbol(item,provider),"isin":item.isin}
