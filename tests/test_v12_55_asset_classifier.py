from investment_analyzer.security.asset_classifier import AssetClassifier


def test_authoritative_metadata_wins():
    r=AssetClassifier().classify('XYZ',metadata={'asset_type':'ETF'})
    assert r.asset_type=='ETF' and r.confidence==100


def test_crypto_symbol_pattern():
    r=AssetClassifier().classify('BTC-USD')
    assert r.asset_type=='CRYPTO'


def test_unknown_is_conservative():
    r=AssetClassifier().classify('UNKNOWN')
    assert r.asset_type=='STOCK'
    assert r.confidence<50
