from investment_analyzer.common.models import (
    BalanceSheet,
    CashFlow,
    FinancialStatements,
    IncomeStatement,
    PriceData,
    PriceHistory,
)
from investment_analyzer.pipeline.financial_data_loader import FinancialSnapshot
from investment_analyzer.pipeline.pipeline import AnalysisPipeline


class Asset:
    def __init__(self, symbol):
        self.symbol = symbol


class AssetLoader:
    def load(self, ticker):
        return Asset(ticker.upper())


class Loader:
    def load(self, symbol):
        history = PriceHistory(
            symbol=symbol,
            dates=list(range(60)),
            open=[100.0 + i for i in range(60)],
            high=[101.0 + i for i in range(60)],
            low=[99.0 + i for i in range(60)],
            close=[100.0 + i for i in range(60)],
            volume=[1_000_000.0] * 60,
        )
        return FinancialSnapshot(
            price=PriceData(symbol=symbol, current=159.0, previous_close=158.0),
            financials=FinancialStatements(
                balance=BalanceSheet(
                    total_assets=1_000_000,
                    current_assets=300_000,
                    current_liabilities=150_000,
                    total_liabilities=400_000,
                    shareholders_equity=600_000,
                    retained_earnings=200_000,
                ),
                income=IncomeStatement(
                    revenue=500_000,
                    gross_profit=200_000,
                    operating_income=100_000,
                    ebit=100_000,
                    net_income=80_000,
                    interest_expense=10_000,
                ),
                cashflow=CashFlow(
                    operating_cash_flow=100_000,
                    capex=-30_000,
                    free_cash_flow=70_000,
                ),
                fiscal_date="2026-06-30",
            ),
            price_provider="fake",
            financials_provider="fake",
            price_provider_symbol=symbol,
            financials_provider_symbol=symbol,
            history=history,
            history_provider="fake",
            history_provider_symbol=symbol,
        )


class FinancialAdapter:
    def run(self, context):
        context.fundamentals = {"score": 80, "available": True}
        context.valuation = {"score": 75, "available": True}
        context.risk = {"score": 70, "available": True}
        return context


class Module:
    def __init__(self, name):
        self.name = name

    def run(self, context):
        return {"score": 50, "available": True, "module": self.name}


class Modules:
    technical = Module("technical")
    comparables = Module("comparables")
    sentiment = Module("sentiment")
    macro = Module("macro")
    porter = Module("porter")
    elliott = Module("elliott")
    dow = Module("dow")
    backtest = Module("backtest")


def test_offline_pipeline_runs_end_to_end_without_network():
    pipeline = AnalysisPipeline(
        providers=object(),
        modules=Modules(),
        financial_loader=Loader(),
        financial_adapter=FinancialAdapter(),
        asset_loader=AssetLoader(),
    )

    context = pipeline.run("FMTY14.MX")

    assert context.asset.symbol == "FMTY14.MX"
    assert context.price.current == 159.0
    assert context.metadata["data_providers"]["history"] == "fake"
    assert context.technical_result["available"] is True
    assert context.fundamentals["score"] == 80
    assert context.valuation["score"] == 75
    assert context.risk["score"] == 70
    assert context.sentiment["available"] is False or isinstance(context.sentiment, dict)
    assert context.metadata["smart_money"]["available"] in (True, False)
    assert context.decision is not None
