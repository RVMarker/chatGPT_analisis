from investment_analyzer.analysis.valuation.bond_engine import BondValuationEngine


def test_bond_ytm_duration_credit_and_real_yield():
    r=BondValuationEngine().calculate(price=98.5,face_value=100,coupon_rate=8,ytm=9,maturity_years=5,duration=4.2,convexity=20,spread_bps=120,credit_rating="BBB",inflation=4,benchmark_yield=7.5,benchmark_name="CETES")
    assert r.modified_duration is not None
    assert r.real_yield_pct > 4
    assert r.yield_spread_bps == 150
    assert r.credit_score == 68
    assert r.total_score is not None


def test_missing_bond_data_is_explicit():
    r=BondValuationEngine().calculate()
    assert r.total_score is None
    assert any("YTM" in x for x in r.warnings)
