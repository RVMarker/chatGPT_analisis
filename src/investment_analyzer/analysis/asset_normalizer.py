"""V12.57 Normalize heterogeneous provider payloads into one internal schema."""
from __future__ import annotations
from typing import Any, Mapping

class AssetDataNormalizer:
    _ALIASES={
        'price':('price','regularMarketPrice','market_price','last_price','lastPrice'),
        'market_cap':('market_cap','marketCap','marketCapitalization'),
        'volume':('volume','regularMarketVolume','volume24h','volume_24h'),
        'pe':('pe','trailingPE','forwardPE'),
        'ev_ebitda':('ev_ebitda','enterpriseToEbitda','enterpriseValueToEBITDA'),
        'ffo_share':('ffo_share','ffoPerShare','ffo_per_share'),
        'affo_share':('affo_share','affoPerShare','affo_per_share'),
        'nav_share':('nav_share','navPerShare','nav_per_share'),
        'distribution_share':('distribution_share','distributionPerShare','dividendPerShare','dividend_per_share'),
        'coupon_rate':('coupon_rate','couponRate','coupon'),
        'yield_to_maturity':('yield_to_maturity','ytm','yield'),
        'maturity_years':('maturity_years','years_to_maturity','yearsToMaturity'),
        'duration':('duration','modified_duration','modifiedDuration'),
        'convexity':('convexity',),
        'credit_score':('credit_score','creditScore'),
        'liquidity_score':('liquidity_score','liquidityScore'),
        'volatility':('volatility','annualizedVolatility'),
        'max_drawdown':('max_drawdown','maxDrawdown'),
        'momentum':('momentum','momentumScore'),
        'trend':('trend','trendScore'),
        'technical_score':('technical_score','technical','technicalScore'),
        'roe':('roe','returnOnEquity'),
        'roic':('roic','returnOnInvestedCapital'),
        'revenue_growth':('revenue_growth','revenueGrowth'),
        'earnings_growth':('earnings_growth','earningsGrowth'),
        'debt_equity':('debt_equity','debtToEquity'),
        'current_ratio':('current_ratio','currentRatio'),
        'dividend_yield':('dividend_yield','dividendYield'),
    }
    def normalize(self,payload:Mapping[str,Any]|None)->dict[str,Any]:
        p=dict(payload or {}); out={}
        nested=[]
        for k in ('financials','fundamentals','quote','metadata'):
            if isinstance(p.get(k),Mapping): nested.append(p[k])
        sources=[p,*nested]
        for canonical,keys in self._ALIASES.items():
            for source in sources:
                for key in keys:
                    if source.get(key) is not None:
                        out[canonical]=source[key]; break
                if canonical in out: break
        out['raw_provider_fields']=sorted(set().union(*(s.keys() for s in sources)))
        return out
