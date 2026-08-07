from investment_analyzer.analysis.valuation.reit_engine import REITValuationEngine
from investment_analyzer.pipeline.macro_production import ProductionMacroModule


def test_reit_reports_valuation_quality_for_proxy_ffo():
    result = REITValuationEngine().calculate(
        ffo=300,
        shares_outstanding=100,
        current_price=20,
        source_quality="FFO_PROXY",
    )
    assert result.valuation_quality == "MEDIUM"


def test_reit_reports_high_quality_for_official_ffo():
    result = REITValuationEngine().calculate(
        ffo=300,
        shares_outstanding=100,
        current_price=20,
        source_quality="FFO_OFFICIAL",
    )
    assert result.valuation_quality == "HIGH"


def test_macro_cross_country_context_is_computed_without_voting():
    us = {"policy_rate": 4.0, "treasury_10y": 4.5}
    mx = {"policy_rate": 6.5, "treasury_10y": 8.05, "inflation_yoy": 3.12}

    cross = ProductionMacroModule._cross_country_context(us, mx)

    assert cross["policy_rate_spread_mx_us"] == 2.5
    assert cross["treasury_10y_spread_mx_us"] == 3.55
    assert cross["mexico_real_rate_ex_post"] == 3.38
