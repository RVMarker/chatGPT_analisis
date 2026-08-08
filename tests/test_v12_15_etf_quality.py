from investment_analyzer.analysis.valuation.etf_engine import ETFValuationEngine


def test_etf_quality_scores_concentration_fee_tracking_and_nav():
    r=ETFValuationEngine().calculate(
        holdings=[{"ticker":"A","weight_pct":20},{"ticker":"B","weight_pct":10},{"ticker":"C","weight_pct":5}],
        expense_ratio=.10, category_expense_ratio=.20, nav_per_share=100, current_price=100.2,
        tracking_difference=.10, sector_concentration=30, geography_concentration=40,
    )
    assert r.top_10_weight_pct == 35
    assert r.concentration_score == 100
    assert r.diversification_score is not None
    assert r.expense_score is not None
    assert r.tracking_score == 90
    assert r.nav_score == 96
    assert r.quality_score is not None


def test_high_concentration_is_penalized():
    r=ETFValuationEngine().calculate(holdings=[{"ticker":"A","weight_pct":80}],expense_ratio=.50)
    assert r.concentration_score == 0
