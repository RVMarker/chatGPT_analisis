from investment_analyzer.providers.provider_bootstrap import build_provider_stack


class FakeYahoo:
    NAME = "yahoo"


class FakeFMP:
    def get_price(self, symbol):
        assert symbol == "FMTY14"
        return {"price": 101}

    def get_balance_sheet(self, symbol): return {}
    def get_income_statement(self, symbol): return {}
    def get_cash_flow(self, symbol): return {}
    def get_company(self, symbol): return {"symbol": symbol}
    def get_news(self, symbol): return []


def test_fmp_mapping_and_fallback_keep_canonical_symbol():
    registry, manager = build_provider_stack(
        yahoo_provider=FakeYahoo(),
        fmp_provider=FakeFMP(),
        symbol_mappings={"FMTY14.MX": {"fmp": "FMTY14"}},
    )

    assert registry.exists("fmp")
    assert manager.provider_symbol("FMTY14.MX", "fmp") == "FMTY14"
    response = manager.execute("fmp", "FMTY14.MX", "get_price")
    assert response.success
    assert response.canonical_symbol == "FMTY14.MX"
    assert response.provider_symbol == "FMTY14"
    assert response.data["price"] == 101
