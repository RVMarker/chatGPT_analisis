from investment_analyzer.common.models import BalanceSheet, CashFlow, FinancialStatements, IncomeStatement, PriceData
from investment_analyzer.pipeline.financial_data_loader import FinancialSnapshot
from investment_analyzer.pipeline.pipeline import AnalysisPipeline


class Asset:
    symbol = "FMTY14.MX"


class AssetLoader:
    def load(self, ticker):
        return Asset()


class Loader:
    def load(self, symbol):
        return FinancialSnapshot(
            price=PriceData(symbol=symbol, current=100),
            financials=FinancialStatements(
                balance=BalanceSheet(), income=IncomeStatement(), cashflow=CashFlow(), fiscal_date="2026-06-30",
            ),
            price_provider="fake", financials_provider="fake",
            price_provider_symbol=symbol, financials_provider_symbol=symbol,
            history=None, history_provider=None, history_provider_symbol=None,
        )


class FinancialAdapter:
    def run(self, context):
        context.fundamentals = {"score": 50}
        context.valuation = {"score": 50, "available": True}
        context.risk = {"score": 50}
        context.metadata["financial_integration"] = {"fundamental_available": True}
        return context


class Recorder:
    def __init__(self, name, calls, value=None):
        self.name, self.calls, self.value = name, calls, value

    def run(self, context):
        self.calls.append(self.name)
        return self.value if self.value is not None else {"score": 50}


class Decision:
    def run(self, context):
        assert context.fundamentals == {"score": 50}
        assert context.valuation == {"score": 50, "available": True}
        assert context.risk == {"score": 50}
        context.decision = {"strategic": "MANTENER", "tactical": "MANTENER"}
        return context.decision


class SmartMoney:
    def analyze(self, history):
        return type("Signal", (), {"as_dict": lambda self: {"score": None, "available": False, "evidence": []}})()


def test_pipeline_runs_modules_in_dependency_order():
    calls = []
    modules = type("Modules", (), {})()
    modules.technical = Recorder("technical", calls)
    modules.comparables = Recorder("comparables", calls)
    modules.sentiment = Recorder("sentiment", calls, value=[])
    modules.macro = Recorder("macro", calls)
    modules.porter = Recorder("porter", calls)
    modules.elliott = Recorder("elliott", calls)
    modules.dow = Recorder("dow", calls)
    modules.backtest = Recorder("backtest", calls)

    pipeline = AnalysisPipeline(
        providers=None,
        modules=modules,
        financial_loader=Loader(),
        financial_adapter=FinancialAdapter(),
        asset_loader=AssetLoader(),
        decision_module=Decision(),
        smart_money_engine=SmartMoney(),
    )
    context = pipeline.run("FMTY14.MX")

    assert context.asset.symbol == "FMTY14.MX"
    assert calls == ["technical", "comparables", "sentiment", "macro", "porter", "elliott", "dow", "backtest"]
    assert context.decision["strategic"] == "MANTENER"
