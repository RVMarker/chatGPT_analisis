"""V12.12 asset-specific analysis policy for stocks, ETFs, REITs, FIBRAs, crypto and bonds."""
from __future__ import annotations
from dataclasses import dataclass
from investment_analyzer.common.enums import AssetType

@dataclass(frozen=True, slots=True)
class AssetAnalysisPolicy:
    asset_type: AssetType
    strategic_modules: tuple[str, ...]
    tactical_modules: tuple[str, ...]
    valuation_model: str
    required_fields: tuple[str, ...]
    contextual_fields: tuple[str, ...]

_POLICIES={
    AssetType.STOCK: AssetAnalysisPolicy(AssetType.STOCK,("fundamental","valuation","risk"),("technical","sentiment","smart_money"),"DCF",("revenue","ebitda","fcf","net_debt","shares_outstanding"),("pe","ev_ebitda","macro")),
    AssetType.ETF: AssetAnalysisPolicy(AssetType.ETF,("valuation","risk"),("technical","sentiment","smart_money"),"ETF_RELATIVE_NAV",("nav","price","aum","expense_ratio"),("tracking_error","premium_discount","macro")),
    AssetType.REIT: AssetAnalysisPolicy(AssetType.REIT,("fundamental","valuation","risk"),("technical","sentiment","smart_money"),"FFO_CAPITALIZATION",("ffo","shares_outstanding","net_debt"),("affo","nav","distribution","cap_rate","macro")),
    AssetType.FIBRA: AssetAnalysisPolicy(AssetType.FIBRA,("fundamental","valuation","risk"),("technical","sentiment","smart_money"),"FFO_CAPITALIZATION",("ffo","shares_outstanding","net_debt"),("affo","nav","distribution","cap_rate","macro")),
    AssetType.CRYPTO: AssetAnalysisPolicy(AssetType.CRYPTO,("valuation","risk"),("technical","sentiment","smart_money"),"CRYPTO_NETWORK_MARKET",("price","volume","market_cap"),("fdv","supply","onchain","macro")),
    AssetType.BOND: AssetAnalysisPolicy(AssetType.BOND,("valuation","risk"),("technical","sentiment"),"BOND_YIELD_DURATION",("price","coupon","maturity","yield_to_maturity"),("duration","convexity","credit_rating","spread","macro")),
}

def normalize_asset_type(value) -> AssetType:
    if isinstance(value,AssetType): return value
    text=str(value or "").strip().upper().replace("-","_").replace(" ","_")
    aliases={"STOCKS":"STOCK","EQUITY":"STOCK","EQUITIES":"STOCK","ETFS":"ETF","REITS":"REIT","FIBRAS":"FIBRA","CRYPTOCURRENCY":"CRYPTO","CRYPTOCURRENCIES":"CRYPTO","BONDS":"BOND","FIXED_INCOME":"BOND","RENTA_FIJA":"BOND"}
    text=aliases.get(text,text)
    try:return AssetType[text]
    except KeyError: raise ValueError(f"Tipo de activo no soportado: {value}")

def get_asset_policy(value) -> AssetAnalysisPolicy:
    return _POLICIES[normalize_asset_type(value)]
