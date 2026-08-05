from investment_analyzer.providers.fmp_provider import FMPProvider


class FakeFMP:
    def get_price(self, symbol):
        assert symbol == "FMTY14"
        return {"price": 100}

    def get_balance_sheet(self, symbol): return {"symbol": symbol}
    def get_income_statement(self, symbol): return {"symbol": symbol}
    def get_cash_flow(self, symbol): return {"symbol": symbol}
    def get_company(self, symbol): return {"symbol": symbol}
    def get_news(self, symbol): return []


def test_fmp_provider_uses_provider_specific_symbol():
    provider = FMPProvider(FakeFMP())
    assert provider.get_price("FMTY14")["price"] == 100
    assert provider.get_company("FMTY14")["symbol"] == "FMTY14"
