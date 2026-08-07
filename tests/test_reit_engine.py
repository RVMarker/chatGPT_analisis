import pytest

from investment_analyzer.analysis.valuation.reit_engine import REITValuationEngine


def test_reit_ffo_capitalization_returns_fair_value_and_score():
    result = REITValuationEngine().calculate(
        ffo=300,
        shares_outstanding=100,
        current_price=20,
        required_yield=0.09,
        growth=0.03,
    )
    assert result.available is True
    assert result.ffo_per_share == 3
    assert result.fair_value_per_share > 0
    assert result.margin_of_safety is not None
    assert 0 <= result.score <= 100


def test_reit_requires_yield_above_growth():
    with pytest.raises(ValueError):
        REITValuationEngine().calculate(
            ffo=300, shares_outstanding=100, current_price=20,
            required_yield=0.03, growth=0.03,
        )


def test_reit_proxy_is_explicitly_labelled():
    result = REITValuationEngine().calculate(
        ffo=300, shares_outstanding=100, current_price=20,
        source_quality="FFO_PROXY",
    )
    assert result.source_quality == "FFO_PROXY"
    assert any("no sustituye AFFO" in warning for warning in result.warnings)


def test_non_positive_ffo_is_unavailable():
    result = REITValuationEngine().calculate(
        ffo=-10, shares_outstanding=100, current_price=20,
    )
    assert result.available is False
    assert result.fair_value_per_share is None
    assert result.score is None
