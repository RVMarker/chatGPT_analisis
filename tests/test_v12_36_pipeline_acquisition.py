from investment_analyzer.pipeline.end_to_end import InvestmentPipeline


def test_pipeline_acquires_and_builds_consensus():
    def yahoo(symbol): return {"regularMarketPrice":14.29,"FFO":0.4541}
    r=InvestmentPipeline().run(symbol="FMTY14.MX",asset_type="FIBRA",fetchers={"yahoo":yahoo},strategic_coverage=100,tactical_coverage=100)
    assert "price" in r.acquisition["fields"]
    assert "ffo" in r.acquisition["fields"]
    assert r.quality["completeness"] < 100
    assert "holdings" not in r.route["required_fields"]


def test_missing_required_data_reduces_completeness():
    def yahoo(symbol): return {"regularMarketPrice":500.0}
    r=InvestmentPipeline().run(symbol="SPY",asset_type="ETF",fetchers={"yahoo":yahoo},strategic_coverage=100,tactical_coverage=100)
    assert r.quality["completeness"] < 100
    assert "holdings" in r.quality["missing_required"]
