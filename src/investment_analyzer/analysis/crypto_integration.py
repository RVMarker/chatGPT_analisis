"""V12.49 crypto specialization and risk-class classification."""
from __future__ import annotations
from typing import Any
from investment_analyzer.analysis.crypto_valuation import CryptoDecisionEngine

class CryptoAnalyzer:
    def __init__(self, engine=None): self.engine=engine or CryptoDecisionEngine()
    @staticmethod
    def classify(payload:dict[str,Any]|None=None)->str:
        p=payload or {}; stable=bool(p.get("stablecoin") or p.get("is_stablecoin")); return "STABLECOIN" if stable else "CRYPTO_SPOT"
    def analyze(self,symbol:str,payload:dict[str,Any]|None=None)->dict[str,Any]:
        p=payload or {}; result=self.engine.analyze(
            market_cap=p.get("market_cap",p.get("marketCap")), volume_24h=p.get("volume_24h",p.get("volume24h")),
            circulating_supply=p.get("circulating_supply",p.get("circulatingSupply")), max_supply=p.get("max_supply",p.get("maxSupply")), total_supply=p.get("total_supply",p.get("totalSupply")),
            volatility=p.get("volatility"), max_drawdown=p.get("max_drawdown",p.get("maxDrawdown")), onchain_score=p.get("onchain_score"), valuation_score=p.get("valuation_score"),
            momentum=p.get("momentum"), trend=p.get("trend"), exchange_flow=p.get("exchange_flow"), smart_money=p.get("smart_money"))
        d=result.as_dict(); d.update({"symbol":symbol,"crypto_type":self.classify(p),"risk_class":"HIGH" if d["strategic_score"]<50 or d["tactical_score"]<40 else "STANDARD"}); return d
