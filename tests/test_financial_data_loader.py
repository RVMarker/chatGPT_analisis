from investment_analyzer.common.models import BalanceSheet, CashFlow, FinancialStatements, IncomeStatement, PriceData
from investment_analyzer.pipeline.financial_data_loader import FinancialDataLoader


class FakeAdapter:
    def price(self, symbol):
        return PriceData(symbol=symbol, current=100)

    def financial_statements(self, symbol):
        return FinancialStatements(
            balance=BalanceSheet(),
            income=IncomeStatement(),
            cashflow=CashFlow(),
            fiscal_date="2026-06-30",
        )


def test_loader_preserves_yahoo_canonical_symbol():
    snapshot = FinancialDataLoader(adapter=FakeAdapter()).load(" fmty14.mx ")
    assert snapshot.price.symbol == "FMTY14.MX"
    assert snapshot.financials.fiscal_date == "2026-06-30"
    assert snapshot.history is None
    assert snapshot.price_provider_symbol == "FMTY14.MX"
