"""V12.33 normalización común de respuestas de proveedores."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Mapping
from investment_analyzer.common.models import ProviderResult

FIELD_ALIASES={
 "price":("price","currentPrice","regularMarketPrice","last","close"),
 "market_cap":("market_cap","marketCap","marketCapitalization"),
 "expense_ratio":("expense_ratio","expenseRatio","annualReportExpenseRatio","management_fee"),
 "benchmark":("benchmark","benchmarkName","indexTracked"),
 "holdings":("holdings","topHoldings","fundHoldings"),
 "ffo":("ffo","FFO","fundsFromOperations"),
 "affo":("affo","AFFO","adjustedFFO"),
 "nav":("nav","NAV","netAssetValue"),
 "yield":("yield","yieldToMaturity","ytm"),
 "coupon":("coupon","couponRate"),
 "maturity":("maturity","maturityDate"),
 "volume":("volume","regularMarketVolume"),
}

class ProviderNormalizer:
    """Convierte nombres de campos de proveedores al vocabulario interno."""
    _utcnow=lambda: datetime.now(timezone.utc)
    @classmethod
    def result(cls,provider,payload,*,success=True,latency_ms=0.0):
        return ProviderResult(provider=provider,timestamp=cls._utcnow(),success=success,latency_ms=max(0.0,float(latency_ms)),payload=payload)
    @staticmethod
    def first_value(data:Mapping[str,Any]|None,*keys:str,default=None):
        if not data:return default
        for key in keys:
            if data.get(key) is not None:return data[key]
        return default
    @classmethod
    def canonical_fields(cls,data:Mapping[str,Any]|None):
        data=data or {}; out={}
        for canonical,aliases in FIELD_ALIASES.items():
            value=cls.first_value(data,*aliases); out[canonical]=value
        return out
    @staticmethod
    def freshness(timestamp:datetime|None,now:datetime|None=None):
        if timestamp is None:return 0.0
        now=now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:timestamp=timestamp.replace(tzinfo=timezone.utc)
        age_days=max(0.0,(now-timestamp).total_seconds()/86400.0)
        if age_days<=1:return 100.0
        if age_days<=7:return 90.0
        if age_days<=30:return 75.0
        if age_days<=90:return 55.0
        if age_days<=365:return 30.0
        return 10.0
