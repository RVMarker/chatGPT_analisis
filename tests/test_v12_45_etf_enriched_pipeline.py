from investment_analyzer.pipeline.end_to_end import InvestmentPipeline


def test_pipeline_uses_enriched_provider_payload_for_etf():
    def yahoo(symbol): return {"regularMarketPrice":500,"totalAssets":2_000_000_000}
    def fmp(symbol): return {"expenseRatio":0.0009,"benchmark":"S&P 500","holdings":[{"symbol":f"H{i}","weight":0.01} for i in range(12)]}
    r=InvestmentPipeline().run(symbol="SPY",asset_type="ETF",fetchers={"yahoo":yahoo,"fmp":fmp})
    etf=r.specialized_analysis["etf"]
    assert etf["expense_ratio"]==0.0009
    assert etf["benchmark"]=="S&P 500"
    assert len(etf["top10"])==10
    assert "score" in etf and 0<=etf["score"]<=100
