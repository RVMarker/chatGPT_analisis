from investment_analyzer.analysis.reit_fibra_valuation import REITFibraValuation


def test_reit_valuation_uses_ffo_and_excludes_pe_from_vote():
    r=REITFibraValuation().evaluate(price=14.29,ffo_share=.4541,nav_share=15.0,payout_ffo=.75,net_debt_ebitda=5.0,interest_coverage=3.0)
    assert r.model=="FFO_AFFO_NAV"
    assert r.fair_value is not None
    assert r.context["p_e"].startswith("CONTEXTO")
    assert r.score>=0 and r.score<=100


def test_reit_missing_cash_flow_is_explicit():
    r=REITFibraValuation().evaluate(price=14.29)
    assert r.fair_value is None
    assert r.score==0
    assert any("FFO/share" in w for w in r.warnings)
