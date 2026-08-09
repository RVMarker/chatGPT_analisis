from investment_analyzer.analysis.etf_analyzer import ETFAnalyzer


def test_etf_top10_and_expense_ratio():
    payload={"price":500,"expense_ratio":0.0009,"benchmark":"S&P 500","totalAssets":1_000_000_000,"holdings":[{"symbol":"A","weight":0.07},{"symbol":"B","weight":0.06},{"symbol":"C","weight":0.05},{"symbol":"D","weight":0.04},{"symbol":"E","weight":0.03},{"symbol":"F","weight":0.03},{"symbol":"G","weight":0.02},{"symbol":"H","weight":0.02},{"symbol":"I","weight":0.02},{"symbol":"J","weight":0.01},{"symbol":"K","weight":0.01}]}
    r=ETFAnalyzer().analyze("SPY",payload)
    assert len(r.top10)==10
    assert r.top10[0]["name"]=="A"
    assert r.expense_ratio==0.0009
    assert round(r.top10_weight,2)==35.0


def test_missing_etf_fields_generate_warnings():
    r=ETFAnalyzer().analyze("TEST",{"price":10})
    assert r.top10==[]
    assert any("Expense ratio" in x for x in r.warnings)
    assert any("TOP 10" in x for x in r.warnings)
