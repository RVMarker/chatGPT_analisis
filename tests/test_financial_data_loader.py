from investment_analyzer.pipeline.financial_data_loader import FinancialDataLoader


class FakeAdapter:
    def price(self, symbol):
        return {"symbol": symbol}

    def financial_statements(self, symbol):
        return {"symbol": symbol}


def test_loader_preserves_yahoo_canonical_symbol():
    snapshot = FinancialDataLoader(adapter=FakeAdapter()).load(" fmty14.mx ")
    assert snapshot.price["symbol"] == "FMTY14.MX"
    assert snapshot.financials["symbol"] == "FMTY14.MX"
