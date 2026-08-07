from investment_analyzer.common.models import BalanceSheet, CashFlow, FinancialStatements, IncomeStatement, PriceData
from investment_analyzer.pipeline.financial_data_loader import FinancialSnapshot
from investment_analyzer.pipeline.pipeline import AnalysisPipeline
from investment_analyzer.providers.provider_manager import ProviderManager


class Asset:
    symbol = "FMTY14.MX"


class AssetLoader:
    def load(self, ticker):
        assert ticker == "FMTY14.MX"
        return Asset()


class Loader:
    def load(self, symbol):
        assert symbol == "FMTY14.MX"
        return FinancialSnapshot(
            price=PriceData(symbol="FMTY14.MX", current=100),
            financials=FinancialStatements(
                balance=BalanceSheet(), income=IncomeStatement(), cashflow=CashFlow(), fiscal_date="2026-06-30"
            ),
            price_provider="fmp", financials_provider="fmp",
            price_provider_symbol="FMTY14", financials_provider_symbol="FMTY14",
            history=None, history_provider=None, history_provider_symbol=None,
        )


class FinancialAdapter:
    def run(self, context):
        context.fundamentals = {"score": 70}
        context.valuation = {"score": 65, "available": True}
        context.risk = {"score": 75}
        return context


class Recorder:
    def __init__(self, name): self.name = name
    def run(self, context): return {"score": 50}


class Decision:
    def run(self, context):
        assert context.metadata["data_providers"] == {
            "price": "fmp", "financials": "fmp",
            "price_symbol": "FMTY14", "financials_symbol": "FMTY14",
            "history": None, "history_symbol": None, "history_length": 0,
        }
        context.decision = {"strategic": "MANTENER"}
        return context.decision


class Modules:
    technical = Recorder("technical")
    comparables = Recorder("comparables")
    sentiment = Recorder("sentiment")
    macro = Recorder("macro")
    porter = Recorder("porter")
    elliott = Recorder("elliott")
    dow = Recorder("dow")
    backtest = Recorder("backtest")


def test_pipeline_uses_injected_financial_loader_and_preserves_provider_trace():
    pipeline = AnalysisPipeline(
        providers=ProviderManager(), modules=Modules(),
        financial_loader=Loader(), asset_loader=AssetLoader(),
        financial_adapter=FinancialAdapter(), decision_module=Decision(),
    )
    result = pipeline.run("FMTY14.MX")
    assert result.price.symbol == "FMTY14.MX"
    assert result.metadata["data_providers"]["price_symbol"] == "FMTY14"
    assert result.metadata["data_providers"]["history_length"] == 0
    assert result.decision["strategic"] == "MANTENER"
