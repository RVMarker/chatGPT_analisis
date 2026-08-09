from investment_analyzer.analysis.decision.decision_engine import DecisionEngine


def test_missing_score_is_nd_and_not_formatted_as_number():
    engine = DecisionEngine()
    result = engine.evaluate(
        strategic_scores={"fundamental": None, "valuation": None, "technical": None, "risk": None},
        tactical_scores={"technical": None, "sentiment": None, "smart_money": None},
        confidence_inputs={},
    )
    assert result.strategic_score is None
    assert result.tactical_score is None
    assert result.strategic_decision == "N/D"
    assert result.tactical_decision == "N/D"
    engine.print_summary(result)


def test_missing_components_are_excluded_from_weighted_average():
    engine = DecisionEngine()
    result = engine.evaluate(
        strategic_scores={"fundamental": 80, "valuation": None, "technical": 60, "risk": 50},
        tactical_scores={"technical": 60, "sentiment": None, "smart_money": 40},
        confidence_inputs={},
    )
    assert result.strategic_score == 67.86
    assert result.strategic_coverage == 75.0
    assert result.tactical_score == 52.86
    assert result.tactical_coverage == 66.67
