from investment_analyzer.providers.data_router import DataAcquisitionRouter


def test_fibra_route_uses_ffo_engine():
    p=DataAcquisitionRouter().plan("FIBRA","FMTY14.MX")
    assert p["valuation_engine"]=="FIBRA_FFO_NAV"
    assert "ffo" in p["optional_fields"]
    assert p["provider_order"][0]=="yahoo"


def test_etf_route_requires_holdings_and_expense_ratio():
    p=DataAcquisitionRouter().plan("ETF","SPY")
    assert "holdings" in p["required_fields"]
    assert "expense_ratio" in p["required_fields"]
    assert p["valuation_engine"]=="ETF_RELATIVE_VALUE"


def test_all_supported_asset_classes_have_routes():
    r=DataAcquisitionRouter()
    for asset in ("STOCK","ETF","REIT","FIBRA","CRYPTO","BOND"):
        assert r.route(asset).asset_type==asset
