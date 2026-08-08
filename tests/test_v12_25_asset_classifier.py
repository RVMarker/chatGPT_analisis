from investment_analyzer.providers.asset_classifier import AssetClassifier

def test_provider_metadata_has_priority():
    r=AssetClassifier().classify("ABC",provider_asset_type="ETF",description="equity fund")
    assert r.asset_type=="ETF" and r.confidence==98.0

def test_fibra_is_detected():
    r=AssetClassifier().classify("FMTY14.MX",description="FIBRA inmobiliaria mexicana")
    assert r.asset_type=="FIBRA"

def test_crypto_is_detected():
    r=AssetClassifier().classify("XYZ-USD",description="cryptocurrency token blockchain")
    assert r.asset_type=="CRYPTO"

def test_unknown_is_not_overconfident():
    r=AssetClassifier().classify("UNKNOWN")
    assert r.asset_type=="STOCK" and r.confidence<50
