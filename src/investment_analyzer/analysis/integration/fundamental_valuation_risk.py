"""V12.17 asset-aware integration boundary."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any, Iterable
from investment_analyzer.analysis.fundamental.fundamental_engine import FundamentalEngine
from investment_analyzer.analysis.risk.risk_engine import RiskEngine
from investment_analyzer.analysis.valuation.dcf_engine import DCFEngine, DCFResult
from investment_analyzer.analysis.valuation.reit_engine import REITValuationEngine
from investment_analyzer.analysis.valuation.etf_engine import ETFValuationEngine
from investment_analyzer.analysis.valuation.crypto_engine import CryptoValuationEngine
from investment_analyzer.common.models import FinancialStatements, PriceData
from investment_analyzer.providers.provenance import DataPoint
from investment_analyzer.providers.provider_confidence import ProviderConfidence

@dataclass(slots=True)
class IntegratedFinancialAnalysis:
    asset_type:str; fundamental:dict[str,Any]; valuation:dict[str,Any]; risk:dict[str,Any]; strengths:list[str]; red_flags:list[str]; provider_validation:dict[str,dict[str,Any]]|None=None; data_quality_score:float=100.0; blocked_fields:list[str]|None=None
    def as_dict(self): return asdict(self)

class FinancialAnalysisIntegrator:
    ALIASES={"STOCK":"STOCK","STOCKS":"STOCK","EQUITY":"STOCK","ETF":"ETF","ETFS":"ETF","REIT":"REIT","REITS":"REIT","FIBRA":"FIBRA","FIBRAS":"FIBRA","CRYPTO":"CRYPTO","CRYPTOS":"CRYPTO","BOND":"BOND","BONDS":"BOND","FIXED_INCOME":"BOND","FIXED-INCOME":"BOND"}
    def __init__(self,fundamental=None,valuation=None,risk=None,reit_valuation=None,etf_valuation=None,crypto_valuation=None,provider_confidence=None): self.fundamental=fundamental or FundamentalEngine(); self.valuation=valuation or DCFEngine(); self.risk=risk or RiskEngine(); self.reit_valuation=reit_valuation or REITValuationEngine(); self.etf_valuation=etf_valuation or ETFValuationEngine(); self.crypto_valuation=crypto_valuation or CryptoValuationEngine(); self.provider_confidence=provider_confidence or ProviderConfidence()
    @classmethod
    def normalize_asset_type(cls,asset_type):
        key=str(asset_type or "STOCK").strip().upper().replace(" ","_")
        if key not in cls.ALIASES: raise ValueError(f"Clase de activo no soportada: {asset_type}")
        return cls.ALIASES[key]
    @staticmethod
    def _points(extra,field,value,provider="normalized",quality="MEDIUM"):
        points=list(extra or [])
        if value is not None and not any(p.field==field and p.provider==provider for p in points): points.append(DataPoint(field,value,provider,quality=quality))
        return points
    def run(self,statements:FinancialStatements,price:PriceData,*,growth_rates=None,wacc=None,terminal_growth=None,net_debt=None,asset_type="STOCK",reit_required_yield=.09,reit_growth=.03,provider_points:Iterable[DataPoint]|None=None,asset_context:dict[str,Any]|None=None):
        if price.current<=0: raise ValueError("El precio actual debe ser positivo")
        asset=self.normalize_asset_type(asset_type); ctx=asset_context or {}; balance,income,cashflow=statements.balance,statements.income,statements.cashflow; debt=net_debt if net_debt is not None else float(balance.long_term_debt or 0)-float(balance.cash or 0); fundamental=self.fundamental.calculate(statements)
        raw={"ffo":cashflow.ffo_official if cashflow.ffo_official is not None else cashflow.ffo_proxy,"affo":cashflow.affo_official,"ebitda":income.ebitda,"net_debt":debt,"interest_expense":income.interest_expense,"property_value":balance.property_value,"shares_outstanding":price.shares_outstanding,"distribution":cashflow.dividends_paid}; points=list(provider_points or []); qualities={"ffo":"HIGH" if cashflow.ffo_official is not None else "LOW_MEDIUM","affo":"HIGH","ebitda":"MEDIUM","net_debt":"MEDIUM","interest_expense":"MEDIUM","property_value":"MEDIUM","shares_outstanding":"MEDIUM","distribution":"MEDIUM"}
        for f,v in raw.items(): points=self._points(points,f,v,quality=qualities[f])
        validation=self.provider_confidence.decide(points,raw.keys()); blocked=[f for f,d in validation.items() if not d.vote_allowed and d.status!="MISSING"]; dq=self.provider_confidence.score(validation); is_property=asset in {"REIT","FIBRA"}; risk=self.risk.calculate(statements,market_value_equity=price.market_cap,is_reit=is_property); warnings=[]; valuation={"available":False,"score":None,"model":"NONE","asset_type":asset,"warnings":[]}
        if asset in {"REIT","FIBRA"}:
            f=validation["ffo"]
            if price.shares_outstanding and f.vote_allowed:
                reit=self.reit_valuation.calculate(ffo=float(f.value),shares_outstanding=float(price.shares_outstanding),current_price=float(price.current),required_yield=reit_required_yield,growth=reit_growth,source_quality="FFO_OFFICIAL" if cashflow.ffo_official is not None else "FFO_PROXY",affo=validation["affo"].value if validation["affo"].vote_allowed else None,distribution=validation["distribution"].value if validation["distribution"].vote_allowed else None,distribution_period=cashflow.dividends_paid_period,distribution_source=cashflow.distribution_source,property_value=validation["property_value"].value if validation["property_value"].vote_allowed else None,net_debt=validation["net_debt"].value if validation["net_debt"].vote_allowed else None,ebitda=validation["ebitda"].value if validation["ebitda"].vote_allowed else None,interest_expense=validation["interest_expense"].value if validation["interest_expense"].vote_allowed else None); valuation=reit.as_dict(); valuation.update({"model":reit.method,"asset_type":asset,"provider_validation":{k:asdict(v) for k,v in validation.items()},"blocked_fields":blocked}); warnings.extend(reit.warnings)
            else: valuation["warnings"]=[f"{asset}: FFO no utilizable; valoración no vota"]; valuation["blocked_fields"]=blocked
        elif asset=="STOCK":
            if growth_rates and wacc is not None and terminal_growth is not None and cashflow.free_cash_flow is not None:
                dcf:DCFResult=self.valuation.calculate(fcf_base=float(cashflow.free_cash_flow),growth_rates=growth_rates,wacc=float(wacc),terminal_growth=float(terminal_growth),net_debt=debt,shares_outstanding=price.shares_outstanding,current_price=price.current); valuation=dcf.as_dict(); valuation.update({"available":dcf.fair_value_per_share is not None,"model":"DCF","asset_type":asset}); warnings.extend(dcf.warnings)
            else: valuation["warnings"]=["STOCK: faltan FCF/assumptions para DCF"]
        elif asset=="ETF":
            etf=self.etf_valuation.calculate(holdings=ctx.get("holdings",[]),expense_ratio=ctx.get("expense_ratio"),nav_per_share=ctx.get("nav_per_share"),current_price=price.current,premium_discount=ctx.get("premium_discount"),tracking_difference=ctx.get("tracking_difference"),tracking_error=ctx.get("tracking_error"),sector_concentration=ctx.get("sector_concentration"),geography_concentration=ctx.get("geography_concentration"),category_expense_ratio=ctx.get("category_expense_ratio"),benchmark=ctx.get("benchmark"),category=ctx.get("category"),benchmark_return=ctx.get("benchmark_return"),etf_return=ctx.get("etf_return"),dividend_yield=ctx.get("dividend_yield"),distribution_frequency=ctx.get("distribution_frequency")); valuation=etf.as_dict(); valuation["asset_type"]=asset; warnings.extend(etf.warnings)
        elif asset=="CRYPTO":
            valuation=self.crypto_valuation.calculate(market_cap=ctx.get("market_cap",price.market_cap),fdv=ctx.get("fdv"),circulating_supply=ctx.get("circulating_supply"),total_supply=ctx.get("total_supply"),max_supply=ctx.get("max_supply"),volume_24h=ctx.get("volume_24h"),active_addresses=ctx.get("active_addresses"),transaction_growth=ctx.get("transaction_growth"),staking_yield=ctx.get("staking_yield"),token_unlock_pct=ctx.get("token_unlock_pct"),holder_concentration_top10=ctx.get("holder_concentration_top10"),fdv_peer_median=ctx.get("fdv_peer_median"),volume_peer_median=ctx.get("volume_peer_median")).as_dict(); valuation["asset_type"]=asset; warnings.extend(valuation.get("warnings",[]))
        elif asset=="BOND": valuation={"available":True,"score":None,"model":"BOND_YIELD_DURATION","asset_type":asset,"ytm":ctx.get("ytm"),"coupon":ctx.get("coupon"),"maturity_years":ctx.get("maturity_years"),"duration":ctx.get("duration"),"convexity":ctx.get("convexity"),"spread":ctx.get("spread"),"credit_rating":ctx.get("credit_rating"),"real_yield":ctx.get("real_yield"),"warnings":[]}
        strengths=list(dict.fromkeys(fundamental.strengths+risk.strengths)); red=list(dict.fromkeys(fundamental.red_flags+risk.red_flags+warnings));
        if blocked:red.append("Campos bloqueados por conflicto de proveedores: "+", ".join(blocked))
        return IntegratedFinancialAnalysis(asset_type=asset,fundamental=fundamental.as_dict(),valuation=valuation,risk=risk.as_dict(),strengths=strengths,red_flags=red,provider_validation={k:asdict(v) for k,v in validation.items()},data_quality_score=dq,blocked_fields=blocked)
