from investment_analyzer.analysis.valuation.reit_engine import REITValuationEngine


def test_reit_sensitivity_has_base_case_and_matrix():
    result = REITValuationEngine().calculate(
        ffo=45.41,
        shares_outstanding=100,
        current_price=14.29,
        required_yield=.09,
        growth=.03,
        source_quality="FFO_PROXY",
        sensitivity_yields=(.08, .09, .10),
        sensitivity_growths=(.02, .03, .04),
    )

    assert result.sensitivity is not None
    assert result.sensitivity["base_case"]["yield"] == .09
    assert result.sensitivity["base_case"]["growth"] == .03
    assert len(result.sensitivity["fair_values"]) == 3
    assert all(len(row) == 3 for row in result.sensitivity["fair_values"].values())


def test_higher_required_yield_reduces_fair_value_and_higher_growth_increases_it():
    result = REITValuationEngine().calculate(
        ffo=45.41,
        shares_outstanding=100,
        current_price=14.29,
        required_yield=.09,
        growth=.03,
        source_quality="FFO_PROXY",
        sensitivity_yields=(.08, .09, .10),
        sensitivity_growths=(.02, .03, .04),
    )
    matrix = result.sensitivity["fair_values"]
    assert matrix["0.0800"]["0.0300"] > matrix["0.0900"]["0.0300"]
    assert matrix["0.0900"]["0.0400"] > matrix["0.0900"]["0.0300"]


def test_sensitivity_does_not_change_base_score():
    result = REITValuationEngine().calculate(
        ffo=45.41,
        shares_outstanding=100,
        current_price=14.29,
        required_yield=.09,
        growth=.03,
        source_quality="FFO_PROXY",
        sensitivity_yields=(.07, .09, .11),
        sensitivity_growths=(.01, .03, .05),
    )
    assert result.fair_value_per_share == result.sensitivity["base_case"]["fair_value"]
