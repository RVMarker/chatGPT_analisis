"""Production composition root for the V11 analyzer."""
from __future__ import annotations

from dataclasses import dataclass

from investment_analyzer.pipeline.decision_module import DecisionModule
from investment_analyzer.pipeline.decision_report import format_decision_report
from investment_analyzer.pipeline.financial_data_loader import FinancialDataLoader
from investment_analyzer.pipeline.financial_modules import FinancialModuleAdapter
from investment_analyzer.pipeline.pipeline import AnalysisPipeline
from investment_analyzer.pipeline.production_modules import UnavailableModule, YahooNewsModule
from investment_analyzer.pipeline.technical_module import TechnicalModule
from investment_analyzer.providers.provider_bootstrap import build_provider_stack
from investment_analyzer.security.asset_loader import AssetLoader


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
    """Build the production stack used by the CLI.

    Modules without a production data source return explicit N/D payloads;
    they never abort the complete analysis or fabricate a neutral score.
    """
    registry, manager = build_provider_stack(
        yahoo_provider=yahoo_provider,
        fmp_provider=fmp_provider,
        symbol_mappings=symbol_mappings,
    )
    data_loader = FinancialDataLoader(provider_manager=manager)

    modules = ModuleBundle(
        technical=TechnicalModule(),
        comparables=UnavailableModule("comparables"),
        sentiment=YahooNewsModule(manager),
        macro=UnavailableModule("macro"),
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
        asset_loader=AssetLoader(),
        decision_module=DecisionModule(),
    )
    return pipeline, manager, registry


def run_application(ticker: str, **kwargs) -> int:
    pipeline, _, _ = build_application(**kwargs)
    context = pipeline.run(ticker)
    print(format_decision_report(context))
    return 0
