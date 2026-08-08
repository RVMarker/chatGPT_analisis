from investment_analyzer.analysis.valuation.crypto_engine import CryptoValuationEngine


def test_crypto_tokenomics_network_liquidity_and_valuation():
    r=CryptoValuationEngine().calculate(market_cap=1_000,fdv=1_500,circulating_supply=60,total_supply=100,max_supply=100,volume_24h=100,active_addresses=50,transaction_growth=20,staking_yield=5,token_unlock_pct=10,holder_concentration_top10=30,fdv_peer_median=2_000,volume_peer_median=50)
    assert r.fdv_to_market_cap==1.5
    assert r.supply_ratio_pct==60
    assert r.volume_to_market_cap_pct==10
    assert r.score_tokenomics is not None
    assert r.score_network is not None
    assert r.score_liquidity is not None
    assert r.score_valuation is not None
    assert r.score_total is not None


def test_crypto_missing_data_is_explicit():
    r=CryptoValuationEngine().calculate(market_cap=100)
    assert r.score_total is not None or r.score_total is None
    assert any("FDV" in x for x in r.warnings)
    assert any("volumen" in x for x in r.warnings)
