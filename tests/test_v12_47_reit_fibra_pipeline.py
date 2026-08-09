from investment_analyzer.pipeline.end_to_end import InvestmentPipeline


def test_fibra_pipeline_uses_specialized_valuation():
    def yahoo(symbol):
        return {"regularMarketPrice":14.29,"ffoPerShare":0.4541,"affoPerShare":0.42,"navPerShare":15.5,"dividendPerShare":0.9,"payoutFFO":0.70,"netDebtToEBITDA":5.0,"interestCoverage":3.0,"capRate":0.08}
    r=InvestmentPipeline().run(symbol="FMTY14.MX",asset_type="FIBRA",fetchers={"yahoo":yahoo})
    rf=r.specialized_analysis["reit_fibra"]
    assert rf["model"]=="FFO_AFFO_NAV"
    assert rf["fair_value"] is not None
    assert rf["context"]["p_e"].startswith("CONTEXTO")
    assert r.decision["strategic"]["specialized_component"]=="REIT_FIBRA"


def test_fibra_does_not_use_pe_as_vote():
    def yahoo(symbol): return {"regularMarketPrice":10,"ffoPerShare":1}
    r=InvestmentPipeline().run(symbol="X.MX",asset_type="FIBRA",fetchers={"yahoo":yahoo})
    assert "p_e" in r.specialized_analysis["reit_fibra"]["context"]
    assert not any("p_e" in key.lower() for key in r.specialized_analysis["reit_fibra"]["components"])
