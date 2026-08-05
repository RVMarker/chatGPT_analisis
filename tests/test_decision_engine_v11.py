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


def test_weights_sum_to_one():
    assert sum(STRATEGIC.values()) == 1.0
    assert sum(TACTICAL.values()) == 1.0


def test_all_strong_is_buy_on_both_horizons():
    engine = DecisionEngine()
    result = engine.evaluate(
        strategic_scores={"fundamental": 100, "valuation": 100, "risk": 100},
        tactical_scores={"technical": 100, "sentiment": 100, "smart_money": 100},
        confidence_inputs=_confidence(),
        contextual={"comparables": 20, "macro": 20},
    )
    assert result.strategic_score == 100
    assert result.tactical_score == 100
    assert result.strategic_decision == "COMPRAR"
    assert result.tactical_decision == "COMPRAR"
    assert result.confidence == 100
    # Context cannot change the verdict.
    assert result.contextual == {"comparables": 20.0, "macro": 20.0}


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
    engine = DecisionEngine()
    result = engine.evaluate(
        strategic_scores={"fundamental": 50, "valuation": 50, "risk": 50},
        tactical_scores={"technical": 50, "sentiment": 50, "smart_money": 50},
        confidence_inputs=_confidence(80),
    )
    assert result.strategic_score == 50
    assert result.tactical_score == 50
    assert result.strategic_decision == "REDUCIR"
    assert result.tactical_decision == "REDUCIR"


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
