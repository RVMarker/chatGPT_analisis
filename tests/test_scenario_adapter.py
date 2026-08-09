from investment_analyzer.analysis.decision.scenario_adapter import normalize_scenarios


def test_missing_scenarios_are_not_invented():
    assert normalize_scenarios({"fair_value_per_share": 130}) == {
        "bear": None,
        "base": 130.0,
        "bull": None,
    }


def test_technical_target_is_not_base_fair_value():
    result = normalize_scenarios({"target_price": 125, "technical": {"target_price": 140}})
    assert result["base"] is None


def test_explicit_bear_base_bull_are_preserved():
    result = normalize_scenarios({"bear_case": 90, "fair_value": 120, "bull_case": 150})
    assert result == {"bear": 90.0, "base": 120.0, "bull": 150.0}
