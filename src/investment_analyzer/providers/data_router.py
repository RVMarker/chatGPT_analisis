"""V12.31 provider/data acquisition routing.

This layer selects the data requirements and provider order by asset class;
it does not silently invent market data when a provider is unavailable.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass(frozen=True, slots=True)
class DataRoute:
    asset_type:str
    providers:tuple[str,...]
    required_fields:tuple[str,...]
    optional_fields:tuple[str,...]
    valuation_engine:str
    def as_dict(self): return asdict(self)

class DataAcquisitionRouter:
    ROUTES={
        "STOCK":DataRoute("STOCK",("yahoo","fmp","alphavantage"),("price","history","income_statement","balance_sheet","cash_flow","shares_outstanding"),("news","analyst_targets","insider_transactions","options"),"DCF_MULTIPLE"),
        "ETF":DataRoute("ETF",("yahoo","fmp"),("price","history","holdings","expense_ratio","benchmark"),("tracking_error","tracking_difference","sector_weights","country_weights","distribution"),"ETF_RELATIVE_VALUE"),
        "REIT":DataRoute("REIT",("yahoo","fmp"),("price","history","income_statement","balance_sheet","cash_flow"),("ffo","affo","nav","net_debt_ebitda","interest_coverage","distribution"),"REIT_FFO_NAV"),
        "FIBRA":DataRoute("FIBRA",("yahoo","fmp"),("price","history","income_statement","balance_sheet","cash_flow"),("ffo","affo","nav","net_debt_ebitda","interest_coverage","distribution"),"FIBRA_FFO_NAV"),
        "CRYPTO":DataRoute("CRYPTO",("coingecko","binance","yahoo"),("price","history","market_cap","volume"),("supply","max_supply","tokenomics","onchain","funding_rate"),"CRYPTO_MARKET_STRUCTURE"),
        "BOND":DataRoute("BOND",("fmp","yahoo"),("price","yield","maturity","coupon"),("duration","credit_rating","ytm","spread","convexity"),"BOND_YIELD_DURATION"),
    }
    def route(self,asset_type):
        key=str(asset_type).upper().replace("EQUITY","STOCK")
        if key not in self.ROUTES: raise ValueError(f"Tipo de activo no soportado: {asset_type}")
        return self.ROUTES[key]
    def plan(self,asset_type,symbol):
        r=self.route(asset_type)
        return {"symbol":symbol,"asset_type":r.asset_type,"provider_order":list(r.providers),"required_fields":list(r.required_fields),"optional_fields":list(r.optional_fields),"valuation_engine":r.valuation_engine}
