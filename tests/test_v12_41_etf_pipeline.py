from investment_analyzer.pipeline.end_to_end import InvestmentPipeline


def test_etf_analysis_is_exposed_by_pipeline():
    def yahoo(symbol):
        return {"regularMarketPrice":500,"expenseRatio":0.0009,"benchmark":"S&P 500","totalAssets":1_000_000_000,
                "holdings":[{"symbol":f"H{i}","weight":0.01} for i in range(12)]}
    r=InvestmentPipeline().run(symbol="SPY",asset_type="ETF",fetchers={"yahoo":yahoo})
    etf=r.specialized_analysis["etf"]
    assert len(etf["top10"])==10
    assert etf["expense_ratio"]==0.0009
    assert etf["benchmark"]=="S&P 500"
