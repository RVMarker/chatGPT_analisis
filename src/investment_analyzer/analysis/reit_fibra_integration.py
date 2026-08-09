"""V12.47 REIT/FIBRA specialized analysis integration."""
from __future__ import annotations
from typing import Any
from investment_analyzer.analysis.reit_fibra_valuation import REITFibraValuation

class REITFibraAnalyzer:
    def __init__(self, valuation=None):
        self.valuation=valuation or REITFibraValuation()

    def analyze(self, symbol: str, payload: dict[str,Any], price: float|None=None) -> dict[str,Any]:
        p=payload or {}
        def first(*keys):
            for k in keys:
                if p.get(k) is not None:return p[k]
            return None
        price=price if price is not None else first("price","regularMarketPrice","last_price")
        result=self.valuation.evaluate(
            price=price,
            ffo_share=first("ffo_share","ffoPerShare","ffo_per_share"),
            affo_share=first("affo_share","affoPerShare","affo_per_share"),
            nav_share=first("nav_share","navPerShare","nav_per_share"),
            distribution_share=first("distribution_share","distributionPerShare","dividendPerShare"),
            payout_ffo=first("payout_ffo","payoutFFO","ffo_payout"),
            net_debt_ebitda=first("net_debt_ebitda","netDebtToEBITDA","net_debt_to_ebitda"),
            interest_coverage=first("interest_coverage","interestCoverage"),
            cap_rate=first("cap_rate","capRate"),
            ffo_multiple=first("ffo_multiple","ffoMultiple") or 17.0,
            affo_multiple=first("affo_multiple","affoMultiple") or 16.0,
            required_return=first("required_return","requiredReturn") or .085,
        )
        d=result.as_dict(); d["symbol"]=symbol; d["price"]=price; return d
