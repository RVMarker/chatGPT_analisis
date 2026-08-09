from investment_analyzer.analysis.etf_analyzer import ETFAnalyzer


def test_etf_analyzer_contains_costs():
    r=ETFAnalyzer().analyze('SPY',{'expense_ratio':.0009,'category_median_expense_ratio':.0015,'tracking_difference':-.03,'tracking_error':.08,'holdings':[{'symbol':'A','weight':.10}]})
    assert r.costs['expense_ratio']==.09
    assert r.costs['expense_premium_vs_category']==-.06
    assert r.top10[0]['name']=='A'
