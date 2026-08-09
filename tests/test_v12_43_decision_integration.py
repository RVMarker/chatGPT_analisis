from investment_analyzer.analysis.decision_integration import SpecializedDecisionIntegrator


def test_etf_specialized_score_replaces_generic_strategic_score_without_double_counting():
    r=SpecializedDecisionIntegrator().integrate(asset_type="ETF",strategic={"score":61.0,"coverage":90},specialized={"etf":{"score":82.5,"coverage":100}})
    assert r["score"]==82.5
    assert r["generic_score"]==61.0
    assert r["specialized_component"]=="ETF"


def test_non_etf_is_unchanged():
    original={"score":61.0,"coverage":90}
    assert SpecializedDecisionIntegrator().integrate(asset_type="STOCK",strategic=original)==original
