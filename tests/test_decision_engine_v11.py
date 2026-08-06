"""Regression tests for the V11 decision engine."""

from investment_analyzer.analysis.decision.decision_engine import DecisionEngine
from investment_analyzer.analysis.decision.decision_weights import STRATEGIC, TACTICAL


def _confidence(value=100):
    return {
        "provider_quality": value,
        "freshness": value,
        "consistency": value,
        "completeness": value,
    }


def _evaluate(score):
    engine = DecisionEngine()
    return engine.evaluate(
        strategic_scores={"fundamental": score, "valuation": score, "risk": score},
        tactical_scores={"technical": score, "sentiment": score, "smart_money": score},
        confidence_inputs=_confidence(),
    )


def test_weights_sum_to_one():
    assert sum(STRATEGIC.values()) == 1.0
    assert sum(TACTICAL.values()) == 1.0


def test_all_strong_is_buy_on_both_horizons():
    result = _evaluate(100)
    assert result.strategic_score == 100
    assert result.tactical_score == 100
    assert result.strategic_decision == "COMPRAR"
    assert result.tactical_decision == "COMPRAR"
    assert result.confidence == 100


def test_macro_and_comparables_do_not_vote():
    engine = DecisionEngine()
    strategic = {"fundamental": 70, "valuation": 70, "risk": 70}
    tactical = {"technical": 70, "sentiment": 70, "smart_money": 70}
    low_context = engine.evaluate(
        strategic, tactical, _confidence(), contextual={"comparables": 0, "macro": 0}
    )
    high_context = engine.evaluate(
        strategic, tactical, _confidence(), contextual={"comparables": 100, "macro": 100}
    )
    assert low_context.strategic_score == high_context.strategic_score == 70
    assert low_context.tactical_score == high_context.tactical_score == 70


def test_neutral_inputs_are_hold():
    result = _evaluate(50)
    assert result.strategic_score == 50
    assert result.tactical_score == 50
    assert result.strategic_decision == "MANTENER"
    assert result.tactical_decision == "MANTENER"


def test_breakdown_is_numeric_and_transparent():
    engine = DecisionEngine()
    result = engine.evaluate(
        strategic_scores={"fundamental": 80, "valuation": 60, "risk": 70},
        tactical_scores={"technical": 90, "sentiment": 50, "smart_money": 40},
        confidence_inputs=_confidence(),
    )
    assert sum(x.weight for x in result.strategic_breakdown) == 1.0
    assert sum(x.weight for x in result.tactical_breakdown) == 1.0
    assert result.strategic_score == 70
    assert result.tactical_score == 72


def test_exact_decision_thresholds_are_stable():
    cases = [
        (100.0, "COMPRAR"),
        (80.0, "COMPRAR"),
        (79.99, "ACUMULAR"),
        (70.0, "ACUMULAR"),
        (69.99, "MANTENER"),
        (50.0, "MANTENER"),
        (49.99, "REDUCIR"),
        (35.0, "REDUCIR"),
        (34.99, "VENDER"),
        (0.0, "VENDER"),
    ]
    for score, expected in cases:
        result = _evaluate(score)
        assert result.strategic_score == score
        assert result.tactical_score == score
        assert result.strategic_decision == expected
        assert result.tactical_decision == expected


def test_missing_components_are_excluded_and_weights_renormalized():
    engine = DecisionEngine()
    result = engine.evaluate(
        strategic_scores={"fundamental": 100, "valuation": None, "risk": 0},
        tactical_scores={"technical": 100, "sentiment": None, "smart_money": 0},
        confidence_inputs=_confidence(),
    )
    assert result.strategic_score == 50
    assert result.tactical_score == 50
    assert result.strategic_decision == "MANTENER"
    assert result.tactical_decision == "MANTENER"
    assert result.strategic_breakdown[0].weight == 2 / 3
    assert result.strategic_breakdown[1].available is False
    assert result.tactical_breakdown[0].weight == 0.75
    assert result.tactical_breakdown[1].available is False


def test_no_available_evidence_returns_no_decision():
    engine = DecisionEngine()
    result = engine.evaluate(
        strategic_scores={"fundamental": None, "valuation": None, "risk": None},
        tactical_scores={"technical": None, "sentiment": None, "smart_money": None},
        confidence_inputs=_confidence(),
    )
    assert result.strategic_score is None
    assert result.tactical_score is None
    assert result.strategic_decision == "N/D"
    assert result.tactical_decision == "N/D"
