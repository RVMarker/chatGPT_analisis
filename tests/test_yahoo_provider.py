from investment_analyzer.providers.yahoo_provider import YahooProvider


class FakeTicker:
    info = {"shortName": "Test"}
    news = [{"title": "test"}]


class FakeYF:
    def Ticker(self, symbol):
        assert symbol == "FMTY14.MX"
        return FakeTicker()


def test_yahoo_provider_uses_canonical_symbol_and_provider_base_contract():
    from investment_analyzer.providers.yahoo_adapter import YahooFinanceAdapter
    provider = YahooProvider(YahooFinanceAdapter(FakeYF()))
    assert provider.NAME == "yahoo"
    assert provider.get_company("fmty14.mx")["shortName"] == "Test"
    assert provider.get_news("FMTY14.MX")[0]["title"] == "test"
