from investment_analyzer.analysis.valuation.reit_engine import REITValuationEngine


def test_reit_reports_affo_payout_and_leverage_without_using_pe():
    result = REITValuationEngine().calculate(
        ffo=300, shares_outstanding=100, current_price=20,
        source_quality="FFO_OFFICIAL", affo=260, distribution=-180,
        distribution_period="annual", distribution_source="reit_distribution",
        net_debt=900, ebitda=300, interest_expense=60,
    )
    assert result.valuation_quality == "HIGH"
    assert result.affo_per_share == 2.6
    assert result.distribution_per_share == 1.8
    assert result.payout_ratio == 0.6
    assert result.distribution_period == "annual"
    assert result.distribution_source == "reit_distribution"
    assert result.net_debt_to_ebitda == 3.0
    assert result.interest_coverage == 5.0
    assert "payout" in result.component_scores


def test_reit_rejects_unverified_distribution_even_when_annual():
    result = REITValuationEngine().calculate(
        ffo=300, shares_outstanding=100, current_price=20,
        source_quality="FFO_OFFICIAL", distribution=-180, distribution_period="annual",
    )
    assert result.distribution_per_share is None
    assert result.payout_ratio is None
    assert "payout" not in result.component_scores
    assert any("no está certificado como distribución FIBRA/REIT" in warning for warning in result.warnings)


def test_reit_rejects_quarterly_distribution_for_annual_ffo_payout():
    result = REITValuationEngine().calculate(
        ffo=300, shares_outstanding=100, current_price=20,
        source_quality="FFO_OFFICIAL", distribution=-45, distribution_period="quarterly",
        distribution_source="reit_distribution",
    )
    assert result.distribution_per_share is None
    assert result.payout_ratio is None
    assert "payout" not in result.component_scores
    assert any("evita mezclar períodos" in warning for warning in result.warnings)


def test_reit_keeps_nav_and_cap_rate_unavailable_when_property_value_is_missing():
    result = REITValuationEngine().calculate(ffo=300, shares_outstanding=100, current_price=20, source_quality="FFO_PROXY")
    assert result.nav_per_share is None
    assert result.cap_rate is None
    assert any("NAV/cap-rate" in warning for warning in result.warnings)


def test_reit_does_not_infer_affo_from_fcf_or_capex():
    result = REITValuationEngine().calculate(ffo=300, shares_outstanding=100, current_price=20, source_quality="FFO_PROXY")
    assert result.affo_per_share is None
    assert any("AFFO oficial no disponible" in warning for warning in result.warnings)
