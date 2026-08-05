"""Main V11 analysis pipeline."""
from __future__ import annotations

from investment_analyzer.analysis.context.analysis_context import AnalysisContext
from investment_analyzer.pipeline.financial_data_loader import FinancialDataLoader
from investment_analyzer.pipeline.financial_modules import FinancialModuleAdapter


class AnalysisPipeline:
    def __init__(self, providers, modules, financial_adapter=None, financial_loader=None):
        self.providers = providers
        self.modules = modules
        self.financial_loader = financial_loader or FinancialDataLoader()
        self.financial_adapter = financial_adapter or FinancialModuleAdapter()

    def run(self, ticker: str) -> AnalysisContext:
        # The input ticker is the canonical Yahoo Finance symbol. Provider-specific
        # nomenclature is handled only inside provider adapters/mappers.
        asset = self.modules.asset.load(ticker)
        context = AnalysisContext(asset=asset)
        snapshot = self.financial_loader.load(ticker)
        context.price = snapshot.price
        context.financials = snapshot.financials

        context.technical = self.modules.technical.run(context)

        # Fundamental + Valuation/DCF + Risk are one atomic financial stage.
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
