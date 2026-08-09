from investment_analyzer.analysis.crypto_valuation import CryptoDecisionEngine


def test_crypto_returns_separate_strategic_and_tactical_scores():
    r=CryptoDecisionEngine().analyze(market_cap=1e11,volume_24h=2e9,circulating_supply=90,max_supply=100,volatility=20,max_drawdown=-30,onchain_score=80,valuation_score=70,momentum=75,trend=80,exchange_flow=65)
    assert 0<=r.strategic_score<=100
    assert 0<=r.tactical_score<=100
    assert r.strategic_coverage==100
    assert r.tactical_coverage==100


def test_crypto_missing_onchain_does_not_zero_score():
    r=CryptoDecisionEngine().analyze(market_cap=1e10,volume_24h=1e8)
    assert r.strategic_coverage<100
    assert any("On-chain" in w for w in r.warnings)
