from investment_analyzer.analysis.bond_analyzer import BondAnalyzer


def test_bond_metrics_and_rate_sensitivity():
    r=BondAnalyzer().analyze('BONO',{'price':98,'face_value':100,'coupon_rate':.08,'ytm':.09,'years_to_maturity':5,'modified_duration':4.2,'convexity':25,'credit_spread':.012,'benchmark_yield':.075,'inflation':.04})
    assert r['coupon_rate']==8.0
    assert r['ytm']==9.0
    assert r['credit_spread_bps']==120
    assert r['yield_spread_vs_benchmark']==1.5
    assert r['real_yield']>0
    assert r['estimated_price_change_100bp_pct'] is not None
