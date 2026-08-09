from investment_analyzer.pipeline.end_to_end import InvestmentPipeline


def test_pipeline_exposes_fibra_route():
    r=InvestmentPipeline().run(symbol="FMTY14.MX",asset_type="FIBRA",strategic_coverage=100,tactical_coverage=100)
    assert r.route["asset_type"]=="FIBRA"
    assert r.route["valuation_engine"]=="FIBRA_FFO_NAV"
    assert "ffo" in r.route["optional_fields"]


def test_pipeline_exposes_etf_route():
    r=InvestmentPipeline().run(symbol="SPY",asset_type="ETF",strategic_coverage=100,tactical_coverage=100)
    assert r.route["asset_type"]=="ETF"
    assert "holdings" in r.route["required_fields"]
    assert "expense_ratio" in r.route["required_fields"]
