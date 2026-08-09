from investment_analyzer.analysis.etf_scoring import ETFDecisionScorer


def test_etf_score_is_transparent_and_normalized():
    a={"expense_ratio":0.0009,"top10_weight":35,"tracking_score":90,"aum":2_000_000_000}
    r=ETFDecisionScorer().score(a,95)
    assert 0<=r.score<=100
    assert set(r.components)=={"cost","diversification","tracking","scale","data_quality"}
    assert abs(sum(x["contribution"] for x in r.components.values())-100)<0.01


def test_missing_cost_does_not_create_fake_negative_signal():
    r=ETFDecisionScorer().score({"top10_weight":30},100)
    assert "cost" not in r.components
    assert any("Expense ratio" in x for x in r.warnings)
