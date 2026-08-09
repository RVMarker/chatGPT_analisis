from investment_analyzer.analysis.etf_costs import ETFCostAnalyzer


def test_cost_and_tracking_metrics():
    r=ETFCostAnalyzer().analyze({'expense_ratio':.001,'category_median_expense_ratio':.002,'tracking_difference':-.12,'tracking_error':.2,'yield':.025})
    assert r['expense_ratio']==.1
    assert r['benchmark_or_category_expense_ratio']==.2
    assert r['expense_premium_vs_category']==-.1
    assert r['yield']==2.5
    assert r['cost_quality'] is not None
