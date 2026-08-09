from investment_analyzer.providers.provider_registry import ProviderRegistry

class FakePrice:
    current=14.29
    market_cap=1000000
    currency="MXN"

class FakeCash:
    ffo_proxy=123.4

class FakeIncome: net_income=100
class FakeBalance: total_assets=1000
class FakeStatements:
    income=FakeIncome(); balance=FakeBalance(); cashflow=FakeCash()

class FakeYahoo:
    def price(self,symbol): return FakePrice()
    def financial_statements(self,symbol): return FakeStatements()


def test_registry_yahoo_bridge_returns_canonical_payload():
    r=ProviderRegistry().register_defaults(FakeYahoo())
    payload=r.yahoo_fetcher("FMTY14.MX")
    assert payload["current"]==14.29
    assert payload["ffo"]==123.4


def test_fetchers_exposes_registered_provider():
    r=ProviderRegistry().register_defaults(FakeYahoo())
    assert "yahoo" in r.fetchers()
