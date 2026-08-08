from investment_analyzer.analysis.valuation.etf_engine import ETFValuationEngine


def test_top10_is_sorted_and_cost_is_reported():
    holdings=[{"ticker":f"A{i}","name":f"Asset {i}","weight_pct":i} for i in range(1,16)]
    r=ETFValuationEngine().calculate(holdings=holdings,expense_ratio=.20,nav_per_share=100,current_price=99.5,tracking_difference=.10,tracking_error=.20,sector_concentration=35,geography_concentration=60,benchmark="TEST")
    assert len(r.top_10)==10
    assert r.top_10[0]["weight_pct"]==15
    assert r.top_10[-1]["weight_pct"]==6
    assert r.expense_ratio_pct==.20
    assert r.top_10_weight_pct==105
    assert any("Top 10" in x for x in r.warnings)


def test_peer_cost_and_tracking_comparison():
    r=ETFValuationEngine().calculate(expense_ratio=.30,peer_expense_median=.20,tracking_difference=.30,peer_tracking_median=.10)
    assert round(r.expense_premium_pct,1)==50.0
    assert round(r.tracking_premium_pct,1)==200.0
