"""V12.55 conservative asset classification from security master/provider metadata."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True,slots=True)
class AssetClassification:
    asset_type:str
    confidence:float
    source:str
    warnings:tuple[str,...]=()

class AssetClassifier:
    ALIASES={'STOCK':'STOCK','EQUITY':'STOCK','SHARE':'STOCK','ETF':'ETF','REIT':'REIT','FIBRA':'FIBRA','CRYPTO':'CRYPTO','CRYPTOCURRENCY':'CRYPTO','TOKEN':'CRYPTO','BOND':'BOND','BONO':'BOND','FIXED_INCOME':'BOND'}
    def classify(self,symbol:str, asset=None, metadata=None)->AssetClassification:
        p=dict(metadata or {}); raw=p.get('asset_type') or p.get('type')
        if raw:
            a=self.ALIASES.get(str(raw).upper().strip().replace('-','_'))
            if a:return AssetClassification(a,100.0,'metadata')
        if asset is not None:
            a=self.ALIASES.get(str(getattr(asset,'asset_type','')).upper().strip().replace('-','_'))
            if a:return AssetClassification(a,100.0,'security_master')
        s=str(symbol).upper().strip()
        if s.endswith('-USD') or s in {'BTC','ETH','SOL','USDT','USDC','XRP','ADA','DOGE'}: return AssetClassification('CRYPTO',90.0,'symbol_pattern')
        if s.endswith('.MX') and any(x in s for x in ('14','15')): return AssetClassification('FIBRA',65.0,'symbol_pattern',('FIBRA inferred from Mexican ticker pattern; verify SecurityMaster.',))
        return AssetClassification('STOCK',35.0,'fallback',('Asset type inferred as STOCK because no authoritative type metadata was available.',))
