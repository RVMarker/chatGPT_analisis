"""V12.52 stock provider-field adapter."""
from __future__ import annotations
from typing import Any
from investment_analyzer.analysis.stock_valuation import StockDecisionEngine

class StockAnalyzer:
    def __init__(self,engine=None): self.engine=engine or StockDecisionEngine()
    def analyze(self,symbol:str,payload:dict[str,Any]|None=None)->dict[str,Any]:
        p=payload or {}
        def f(*keys):
            for k in keys:
                if p.get(k) is not None:return p[k]
            return None
        r=self.engine.analyze(price=f("price","regularMarketPrice","last_price"),dcf_value=f("dcf_value","dcfFairValue"),pe=f("pe","trailingPE"),peer_pe=f("peer_pe","peerMedianPE"),peg=f("peg","pegRatio"),roe=f("roe","returnOnEquity"),roic=f("roic","returnOnInvestedCapital"),revenue_growth=f("revenue_growth","revenueGrowth"),earnings_growth=f("earnings_growth","earningsGrowth"),debt_equity=f("debt_equity","debtToEquity"),current_ratio=f("current_ratio","currentRatio"),dividend_yield=f("dividend_yield","dividendYield"),technical=f("technical_score","technical"),momentum=f("momentum"),trend=f("trend"),volatility=f("volatility"),liquidity=f("liquidity_score","liquidity"))
        d=r.as_dict(); d["symbol"]=symbol; return d
