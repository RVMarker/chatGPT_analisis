"""Main V11 analysis pipeline."""
from __future__ import annotations

from investment_analyzer.analysis.context.analysis_context import AnalysisContext
from investment_analyzer.pipeline.financial_modules import FinancialModuleAdapter


class AnalysisPipeline:
    def __init__(self, providers, modules, financial_adapter=None):
        self.providers = providers
        self.modules = modules
        self.financial_adapter = financial_adapter or FinancialModuleAdapter()

    def run(self, ticker: str) -> AnalysisContext:
        context = AnalysisContext(asset=self.modules.asset.load(ticker))
        context.technical = self.modules.technical.run(context)

        # Fundamental + Valuation/DCF + Risk are one atomic financial stage.
        # This prevents duplicated calculations and keeps their outputs coherent.
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
