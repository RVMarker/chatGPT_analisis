from investment_analyzer.providers.instrument_identity import InstrumentIdentityRegistry


def test_provider_ticker_is_not_canonical_identity():
    r=InstrumentIdentityRegistry()
    item=r.register(asset_type="FIBRA",symbol="FMTY14.MX",country="MX",isin="MXCFFM010001",provider_symbols={"yahoo":"FMTY14.MX","provider_x":"FMTY14"},aliases=["FMTY14","FMTY"])
    assert item.canonical_id == "FIBRA:ISIN:MXCFFM010001"
    assert r.provider_symbol(item,"yahoo") == "FMTY14.MX"
    assert r.provider_symbol(item,"provider_x") == "FMTY14"
    assert r.resolve(symbol="FMTY14.MX",provider="yahoo").canonical_id == item.canonical_id
    assert r.resolve(symbol="FMTY",provider="provider_x").canonical_id == item.canonical_id


def test_asset_aliases_are_normalized():
    r=InstrumentIdentityRegistry()
    assert r.normalize_asset_type("equity") == "STOCK"
    assert r.normalize_asset_type("fibra") == "FIBRA"
