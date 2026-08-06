"""Main V11 analysis pipeline."""
from __future__ import annotations

from investment_analyzer.analysis.context.analysis_context import AnalysisContext
from investment_analyzer.pipeline.financial_data_loader import FinancialDataLoader
from investment_analyzer.pipeline.financial_modules import FinancialModuleAdapter
from investment_analyzer.providers.provider_manager import ProviderManager
from investment_analyzer.security.asset_loader import AssetLoader


class AnalysisPipeline:
    def __init__(self, providers, modules, financial_adapter=None, financial_loader=None, asset_loader=None):
        self.providers = providers
        self.modules = modules
        self.asset_loader = asset_loader or AssetLoader()
        self.financial_loader = financial_loader or self._build_financial_loader(providers)
        self.financial_adapter = financial_adapter or FinancialModuleAdapter()

    @staticmethod
    def _build_financial_loader(providers):
        """Use the application ProviderManager when one is supplied."""
        if isinstance(providers, ProviderManager):
            return FinancialDataLoader(provider_manager=providers)
        return FinancialDataLoader()

    def run(self, ticker: str) -> AnalysisContext:
        # The user-facing ticker is the canonical Yahoo Finance symbol.
        # Provider-specific nomenclature stays behind SecurityMaster/adapters.
        asset = self.asset_loader.load(ticker)
        context = AnalysisContext(asset=asset)
        snapshot = self.financial_loader.load(asset.symbol)
        context.price = snapshot.price
        context.financials = snapshot.financials
        context.metadata["data_providers"] = {
            "price": snapshot.price_provider,
            "financials": snapshot.financials_provider,
            "price_symbol": snapshot.price_provider_symbol,
            "financials_symbol": snapshot.financials_provider_symbol,
        }

        context.technical = self.modules.technical.run(context)
        self.financial_adapter.run(context)
        context.comparables = self.modules.comparables.run(context)
        context.sentiment = self.modules.sentiment.run(context)
        context.macro = self.modules.macro.run(context)
        context.porter = self.modules.porter.run(context)
        context.elliott = self.modules.elliott.run(context)
        context.dow = self.modules.dow.run(context)
        context.backtest = self.modules.backtest.run(context)
        context.decision = self.modules.decision.run(context)
        return context
