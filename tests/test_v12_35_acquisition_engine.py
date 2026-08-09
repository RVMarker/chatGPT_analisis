from investment_analyzer.providers.acquisition_engine import MultiProviderAcquisitionEngine


def test_fibra_acquisition_normalizes_price_and_ffo():
    def yahoo(symbol): return {"regularMarketPrice":14.29,"FFO":0.4541}
    r=MultiProviderAcquisitionEngine().acquire(symbol="FMTY14.MX",asset_type="FIBRA",fetchers={"yahoo":yahoo})
    assert r.provider_used["price"]=="yahoo"
    assert r.provider_used["ffo"]=="yahoo"
    assert r.fields["price"][0]["value"]==14.29
    assert r.fields["ffo"][0]["value"]==0.4541


def test_required_missing_is_reported():
    def yahoo(symbol): return {"regularMarketPrice":14.29}
    r=MultiProviderAcquisitionEngine().acquire(symbol="SPY",asset_type="ETF",fetchers={"yahoo":yahoo})
    assert "holdings" in r.missing_required
    assert "expense_ratio" in r.missing_required
