from investment_analyzer.analysis.decision.decision_report_adapter import DecisionReportAdapter


def test_report_adapter_preserves_two_horizons_and_weights():
    r=DecisionReportAdapter().build(
        asset_type="ETF",
        strategic={"verdict":"BUY","score":78.5,"coverage_pct":100,"breakdown":[{"factor":"quality","score":80,"weight_pct":35},{"factor":"valuation","score":76,"weight_pct":65}]},
        tactical={"verdict":"HOLD","score":54,"coverage_pct":80,"breakdown":[{"factor":"technical","score":54,"weight_pct":100}]},
        data_quality_score=95,
        context={"benchmark":"S&P 500"},
    )
    assert r.asset == "ETF"
    assert r.strategic["score"] == 78.5
    assert r.strategic["breakdown"][0]["contribution"] == 28
    assert r.tactical["coverage_pct"] == 80
    assert r.quality["decision_confidence_pct"] == 76
    assert r.context["benchmark"] == "S&P 500"


def test_context_is_not_part_of_breakdown():
    r=DecisionReportAdapter().build(asset_type="BOND", strategic={"score":60,"coverage_pct":100,"verdict":"HOLD","breakdown":[]}, tactical={"score":50,"coverage_pct":100,"verdict":"HOLD","breakdown":[]}, context={"banxico":6.5,"curve":"NORMAL"})
    assert r.strategic["breakdown"] == []
    assert "banxico" in r.context
