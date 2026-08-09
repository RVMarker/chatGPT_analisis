from investment_analyzer.analysis.bond_valuation import BondDecisionEngine


def test_bond_fair_value_and_separate_horizons():
    r=BondDecisionEngine().analyze(price=98,face=100,coupon_rate=.08,yield_to_maturity=.07,maturity_years=5,duration=4,credit_score=90,liquidity_score=80,inflation=3,spread=2,momentum=60)
    assert r.fair_price is not None
    assert 0<=r.strategic_score<=100 and 0<=r.tactical_score<=100
    assert r.strategic_coverage==100 and r.tactical_coverage==100


def test_bond_missing_duration_is_explicit():
    r=BondDecisionEngine().analyze(price=100,coupon_rate=.08,yield_to_maturity=.07,maturity_years=5)
    assert r.rate_sensitivity is None
    assert any("Duration" in w for w in r.warnings)
