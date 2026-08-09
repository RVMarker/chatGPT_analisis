from investment_analyzer.analysis.crypto_integration import CryptoAnalyzer


def test_crypto_spot_classification_and_scores():
    r=CryptoAnalyzer().analyze("BTC-USD",{"market_cap":1e12,"volume_24h":2e10,"circulating_supply":19,"max_supply":21,"volatility":20,"max_drawdown":-25,"onchain_score":80,"valuation_score":70,"momentum":75,"trend":80,"exchange_flow":65})
    assert r["crypto_type"]=="CRYPTO_SPOT"
    assert 0<=r["strategic_score"]<=100
    assert 0<=r["tactical_score"]<=100


def test_stablecoin_classification():
    r=CryptoAnalyzer().analyze("USDT-USD",{"stablecoin":True,"market_cap":1e10,"volume_24h":1e9})
    assert r["crypto_type"]=="STABLECOIN"
