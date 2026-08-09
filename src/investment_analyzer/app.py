"""Production composition root for the V12 analyzer."""
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping

from investment_analyzer.pipeline.decision_module import DecisionModule
from investment_analyzer.pipeline.decision_report import render_decision_report
from investment_analyzer.pipeline.financial_data_loader import FinancialDataLoader
from investment_analyzer.pipeline.financial_modules import FinancialModuleAdapter
from investment_analyzer.pipeline.pipeline import AnalysisPipeline
from investment_analyzer.pipeline.production_modules import UnavailableModule, YahooNewsModule
from investment_analyzer.pipeline.comparables_production import ProductionComparablesModule
from investment_analyzer.pipeline.macro_production import ProductionMacroModule
from investment_analyzer.pipeline.technical_module import TechnicalModule
from investment_analyzer.pipeline.trade_plan_report import render_trade_plan
from investment_analyzer.providers.provider_bootstrap import build_provider_stack
from investment_analyzer.security.asset_loader import AssetLoader
from investment_analyzer.security.security_master import SecurityMaster
from investment_analyzer.analysis.decision.trade_plan import build_trade_plan


@dataclass(slots=True)
class ModuleBundle:
    technical: object
    comparables: object
    sentiment: object
    macro: object
    porter: object
    elliott: object
    dow: object
    backtest: object


def build_application(symbol_mappings=None, yahoo_provider=None, fmp_provider=None):
    security_master = SecurityMaster()
    security_master.seed_production_defaults()
    registry, manager = build_provider_stack(
        yahoo_provider=yahoo_provider,
        fmp_provider=fmp_provider,
        symbol_mappings=symbol_mappings,
        security_master=security_master,
    )
    data_loader = FinancialDataLoader(provider_manager=manager)
    modules = ModuleBundle(
        technical=TechnicalModule(),
        comparables=ProductionComparablesModule(manager),
        sentiment=YahooNewsModule(manager),
        macro=ProductionMacroModule(),
        porter=UnavailableModule("porter"),
        elliott=UnavailableModule("elliott"),
        dow=UnavailableModule("dow"),
        backtest=UnavailableModule("backtest"),
    )
    pipeline = AnalysisPipeline(
        providers=manager,
        modules=modules,
        financial_adapter=FinancialModuleAdapter(),
        financial_loader=data_loader,
        asset_loader=AssetLoader(security_master=security_master),
        decision_module=DecisionModule(),
    )
    return pipeline, manager, registry


def _find_number(value, names):
    wanted = {str(x).lower() for x in names}
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key).lower() in wanted:
                try:
                    number = float(item)
                    if number > 0:
                        return number
                except (TypeError, ValueError):
                    pass
        for item in value.values():
            found = _find_number(item, wanted)
            if found is not None:
                return found
    elif isinstance(value, (list, tuple)):
        for item in value:
            found = _find_number(item, wanted)
            if found is not None:
                return found
    return None


def attach_trade_plan(context, capital=5000.0, risk_pct=0.02, max_position_pct=0.25):
    price_data = context.price
    price = getattr(price_data, "current", None) if price_data is not None else None
    valuation = context.valuation or {}
    technical = context.technical or {}
    context.trade_plan = build_trade_plan(
        price=price,
        fair_value=_find_number(valuation, ("fair_value_per_share", "fair_value", "intrinsic_value")),
        bear_value=_find_number(valuation, ("bear_value", "bear_case", "bear_fair_value")),
        bull_value=_find_number(valuation, ("bull_value", "bull_case", "bull_fair_value")),
        support=_find_number(technical, ("support", "support_level", "nearest_support")),
        resistance=_find_number(technical, ("resistance", "resistance_level", "nearest_resistance")),
        atr=_find_number(technical, ("atr", "atr14", "average_true_range")),
        capital=capital,
        risk_pct=risk_pct,
        max_position_pct=max_position_pct,
    )
    return context.trade_plan


def run_application(ticker: str, capital=5000.0, risk_pct=0.02, max_position_pct=0.25, **kwargs) -> int:
    pipeline, _, _ = build_application(**kwargs)
    context = pipeline.run(ticker)
    attach_trade_plan(context, capital=capital, risk_pct=risk_pct, max_position_pct=max_position_pct)
    print(render_decision_report(context))
    print(render_trade_plan(context.trade_plan))
    return 0
