from investment_analyzer.common.models import BalanceSheet, CashFlow, FinancialStatements, IncomeStatement, PriceData
from investment_analyzer.pipeline.financial_data_loader import FinancialDataLoader
from investment_analyzer.providers.provider_bootstrap import build_provider_stack


def _financials():
    return FinancialStatements(
        balance=BalanceSheet(), income=IncomeStatement(), cashflow=CashFlow(), fiscal_date="2026-06-30"
    )


class FakeYahoo:
    NAME = "yahoo"

    def get_price(self, symbol):
        raise RuntimeError("Yahoo unavailable")

    def get_financial_statements(self, symbol):
        raise RuntimeError("Yahoo unavailable")


class FakeFMP:
    def get_price(self, symbol):
        assert symbol == "FMTY14"
        return PriceData(symbol="FMTY14.MX", current=101)

    def get_financial_statements(self, symbol):
        assert symbol == "FMTY14"
        return _financials()


def test_loader_falls_back_to_fmp_and_keeps_provider_traceability():
    _, manager = build_provider_stack(
        yahoo_provider=FakeYahoo(),
        fmp_provider=FakeFMP(),
        symbol_mappings={"FMTY14.MX": {"fmp": "FMTY14"}},
    )
    snapshot = FinancialDataLoader(provider_manager=manager).load(" fmty14.mx ")
    assert snapshot.price.current == 101
    assert snapshot.price_provider == "fmp"
    assert snapshot.financials_provider == "fmp"
    assert snapshot.price_provider_symbol == "FMTY14"
    assert snapshot.financials_provider_symbol == "FMTY14"
    assert snapshot.price.symbol == "FMTY14.MX"
