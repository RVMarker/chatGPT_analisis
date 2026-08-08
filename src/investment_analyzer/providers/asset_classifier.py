"""Best-effort asset-class classifier; provider evidence has priority."""
from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass(slots=True)
class AssetClassification:
    asset_type:str; confidence:float; method:str; symbol:str; evidence:list[str]; candidates:list[tuple[str,float]]
    def as_dict(self): return asdict(self)

class AssetClassifier:
    TYPES=("STOCK","ETF","REIT","FIBRA","CRYPTO","BOND")
    def classify(self,symbol,*,provider_asset_type=None,quote_type=None,description=None,metadata=None):
        s=str(symbol or "").strip().upper(); text=" ".join(str(x or "") for x in (description,metadata)).upper(); evidence=[]
        if provider_asset_type:
            p=str(provider_asset_type).upper().replace("EQUITY","STOCK").replace("FUND","ETF")
            if p in self.TYPES:return AssetClassification(p,98.0,"provider",s,[f"provider_asset_type={p}"],[(p,98.0)])
        scores={x:0.0 for x in self.TYPES}
        rules=(("ETF",("ETF","EXCHANGE TRADED FUND"),"ETF metadata",80),("REIT",("REIT","REAL ESTATE INVESTMENT TRUST"),"REIT metadata",75),("FIBRA",("FIBRA","FIBRA INMOBILIARIA"),"FIBRA metadata",85),("CRYPTO",("CRYPTO","CRYPTOCURRENCY","TOKEN","BLOCKCHAIN"),"crypto metadata",85),("BOND",("BOND","GOVERNMENT SECURITY","TREASURY","CETE","BONO"),"bond metadata",85))
        for asset,keys,msg,points in rules:
            if any(k in text for k in keys):scores[asset]+=points;evidence.append(msg)
        if str(quote_type or "").upper() in {"ETF","MUTUALFUND"}:scores["ETF"]+=20
        if s.endswith(("-USD","USDT","BTC","ETH")):scores["CRYPTO"]+=20
        ranked=sorted(scores.items(),key=lambda x:x[1],reverse=True); top,second=ranked[0],ranked[1]
        if top[1]==0:return AssetClassification("STOCK",45.0,"heuristic_default",s,["sin evidencia suficiente"],[("STOCK",45.0)])
        conf=min(95.0,top[1]+max(0,top[1]-second[1])*.25)
        return AssetClassification(top[0],round(conf,2),"metadata_heuristic",s,evidence,[(a,round(v,2)) for a,v in ranked if v>0])
