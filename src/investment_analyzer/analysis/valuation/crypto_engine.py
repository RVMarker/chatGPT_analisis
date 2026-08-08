"""Crypto-specific valuation, tokenomics, network and liquidity analysis."""
from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass(slots=True)
class CryptoValuation:
    model:str; market_cap:float|None; fdv:float|None; fdv_to_market_cap:float|None
    circulating_supply:float|None; total_supply:float|None; max_supply:float|None
    supply_ratio_pct:float|None; volume_24h:float|None; volume_to_market_cap_pct:float|None
    active_addresses:float|None; transaction_growth_pct:float|None; staking_yield_pct:float|None
    token_unlock_pct:float|None; holder_concentration_top10_pct:float|None
    score_tokenomics:float|None; score_network:float|None; score_liquidity:float|None
    score_valuation:float|None; score_total:float|None; warnings:list[str]
    def as_dict(self): return asdict(self)

class CryptoValuationEngine:
    def calculate(self, *, market_cap=None, fdv=None, circulating_supply=None, total_supply=None,
                  max_supply=None, volume_24h=None, active_addresses=None, transaction_growth=None,
                  staking_yield=None, token_unlock_pct=None, holder_concentration_top10=None,
                  fdv_peer_median=None, volume_peer_median=None):
        fmc=None if market_cap in (None,0) or fdv is None else float(fdv)/float(market_cap)
        supply_ratio=None if not max_supply or circulating_supply is None else float(circulating_supply)/float(max_supply)*100
        turnover=None if not market_cap or volume_24h is None else float(volume_24h)/float(market_cap)*100
        warnings=[]
        for value,msg in ((market_cap,"market cap"),(fdv,"FDV"),(circulating_supply,"circulating supply"),(volume_24h,"volumen 24h"),(active_addresses,"actividad de red"),(holder_concentration_top10,"concentración Top 10 holders")):
            if value is None: warnings.append(f"CRYPTO: {msg} no disponible")
        token=[]
        if supply_ratio is not None: token.append(max(0,min(100,supply_ratio)))
        if fmc is not None: token.append(max(0,min(100,100-(fmc-1)*25)))
        if token_unlock_pct is not None: token.append(max(0,min(100,100-float(token_unlock_pct)*2)))
        if holder_concentration_top10 is not None: token.append(max(0,min(100,100-float(holder_concentration_top10))))
        score_tokenomics=round(sum(token)/len(token),2) if token else None
        network=[]
        if active_addresses is not None: network.append(70.0)
        if transaction_growth is not None: network.append(max(0,min(100,50+float(transaction_growth))))
        score_network=round(sum(network)/len(network),2) if network else None
        liquidity=[]
        if turnover is not None: liquidity.append(max(0,min(100,turnover*5)))
        score_liquidity=round(sum(liquidity)/len(liquidity),2) if liquidity else None
        valuation=[]
        if fdv_peer_median and fdv is not None: valuation.append(max(0,min(100,100-(float(fdv)/float(fdv_peer_median)-1)*50)))
        if volume_peer_median and volume_24h is not None: valuation.append(max(0,min(100,float(volume_24h)/float(volume_peer_median)*50)))
        score_valuation=round(sum(valuation)/len(valuation),2) if valuation else None
        comps=[x for x in (score_tokenomics,score_network,score_liquidity,score_valuation) if x is not None]
        total=round(sum(comps)/len(comps),2) if comps else None
        return CryptoValuation("CRYPTO_NETWORK_MARKET",market_cap,fdv,fmc,circulating_supply,total_supply,max_supply,supply_ratio,volume_24h,turnover,active_addresses,transaction_growth,staking_yield,token_unlock_pct,holder_concentration_top10,score_tokenomics,score_network,score_liquidity,score_valuation,total,warnings)
