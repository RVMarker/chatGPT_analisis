from investment_analyzer.analysis.valuation.etf_engine import ETFValuationEngine


def test_etf_returns_top_10_by_weight_and_admin_cost():
    holdings=[{"ticker":f"T{i}","name":f"Asset {i}","weight_pct":i} for i in range(1,13)]
    r=ETFValuationEngine().calculate(holdings=holdings,expense_ratio=0.20,nav_per_share=100,current_price=101)
    assert len(r.top_10)==10
    assert r.top_10[0]["ticker"]=="T11"
    assert r.top_10[-1]["ticker"]=="T2"
    assert r.expense_ratio_pct==0.20
    assert r.premium_discount_pct==1.0
    assert r.top_10_weight_pct==65


def test_etf_missing_composition_and_fee_is_explicit():
    r=ETFValuationEngine().calculate()
    assert r.top_10==[]
    assert r.expense_ratio_pct is None
    assert any("composición" in x.lower() for x in r.warnings)
    assert any("administración" in x.lower() for x in r.warnings)
