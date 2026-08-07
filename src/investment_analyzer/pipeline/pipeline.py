"""Main V11 analysis pipeline."""
from __future__ import annotations

from collections.abc import Mapping

from investment_analyzer.analysis.context.analysis_context import AnalysisContext
from investment_analyzer.analysis.tactical.sentiment_engine import SentimentEngine
from investment_analyzer.analysis.tactical.smart_money_engine import SmartMoneyEngine
from investment_analyzer.analysis.technical.technical_module_v11 import TechnicalAnalysisV11
from investment_analyzer.pipeline.decision_module import DecisionModule
from investment_analyzer.pipeline.financial_data_loader import FinancialDataLoader
from investment_analyzer.pipeline.financial_modules import FinancialModuleAdapter
from investment_analyzer.providers.provider_manager import ProviderManager
from investment_analyzer.security.asset_loader import AssetLoader


class AnalysisPipeline:
    def __init__(self, providers, modules, financial_adapter=None, financial_loader=None,
                 asset_loader=None, decision_module=None, technical_analyzer=None,
                 sentiment_engine=None, smart_money_engine=None):
        self.providers = providers
        self.modules = modules
        self.asset_loader = asset_loader or AssetLoader()
        self.financial_loader = financial_loader or self._build_financial_loader(providers)
        self.financial_adapter = financial_adapter or FinancialModuleAdapter()
        self.decision_module = decision_module or DecisionModule()
        self.technical_analyzer = technical_analyzer or TechnicalAnalysisV11()
        self.sentiment_engine = sentiment_engine or SentimentEngine()
        self.smart_money_engine = smart_money_engine or SmartMoneyEngine()

    @staticmethod
    def _build_financial_loader(providers):
        if isinstance(providers, ProviderManager):
            return FinancialDataLoader(provider_manager=providers)
        return FinancialDataLoader()

    @staticmethod
    def _extract_news(value):
        """Extract normalized news records without inventing news data."""
        if value is None:
            return []
        if isinstance(value, Mapping):
            for key in ("news", "items", "records", "evidence"):
                candidate = value.get(key)
                if isinstance(candidate, (list, tuple)):
                    return candidate
            return []
        if isinstance(value, (list, tuple)):
            return value
        return []

    def run(self, ticker: str) -> AnalysisContext:
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
            "history": snapshot.history_provider,
            "history_symbol": snapshot.history_provider_symbol,
            "history_length": len(snapshot.history) if snapshot.history is not None else 0,
        }

        if snapshot.history is not None:
            technical_result = self.technical_analyzer.analyze(snapshot.history)
            context.technical_result = technical_result.metadata
            context.technical = {
                "score": technical_result.score,
                "explanation": technical_result.explanation,
                "warnings": technical_result.warnings,
                "indicators": technical_result.metadata.get("indicators", {}),
                "component_scores": technical_result.metadata.get("component_scores", {}),
                "available": technical_result.metadata.get("available", False),
            }
        else:
            context.technical = self.modules.technical.run(context)
            context.technical_result = context.technical

        self.financial_adapter.run(context)
        context.comparables = self.modules.comparables.run(context)

        # Preserve the existing sentiment module as the source of news records,
        # then normalize those records through the evidence-based V11 engine.
        existing_sentiment = self.modules.sentiment.run(context)
        sentiment_signal = self.sentiment_engine.analyze(self._extract_news(existing_sentiment))
        context.sentiment = sentiment_signal.as_dict()
        context.metadata["sentiment_evidence"] = context.sentiment.get("evidence", [])
        context.metadata["sentiment_provider"] = existing_sentiment.get("provider") if isinstance(existing_sentiment, Mapping) else None
        context.metadata["sentiment_provider_symbol"] = existing_sentiment.get("provider_symbol") if isinstance(existing_sentiment, Mapping) else None
        context.metadata["sentiment_raw_count"] = existing_sentiment.get("raw_count", 0) if isinstance(existing_sentiment, Mapping) else 0
        context.metadata["sentiment_normalized_count"] = existing_sentiment.get("normalized_count", 0) if isinstance(existing_sentiment, Mapping) else 0

        smart_money_signal = self.smart_money_engine.analyze(snapshot.history)
        context.metadata["smart_money"] = smart_money_signal.as_dict()
        context.metadata["smart_money_evidence"] = context.metadata["smart_money"].get("evidence", [])

        context.macro = self.modules.macro.run(context)
        context.porter = self.modules.porter.run(context)
        context.elliott = self.modules.elliott.run(context)
        context.dow = self.modules.dow.run(context)
        context.backtest = self.modules.backtest.run(context)

        self.decision_module.run(context)
        return context
