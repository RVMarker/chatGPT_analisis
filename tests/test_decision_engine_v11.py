"""Regression tests for the transparent V11 decision engine."""

from investment_analyzer.analysis.decision.decision_engine import DecisionEngine


def test_strategic_weights_sum_to_one():
    from investment_analyzer.analysis.decision.decision_engine import STRATEGIC_WEIGHTS

    assert sum(STRATEGIC_WEIGHTS.values()) == 1.0


def test_tactical_weights_sum_to_one():
    from investment_analyzer.analysis.decision.decision_engine import TACTICAL_WEIGHTS

    assert sum(TACTICAL_WEIGHTS.values()) == 1.0


def test_strategic_buy_when_all_inputs_are_strong():
    engine = DecisionEngine()
    result = engine.evaluate(
        strategic_scores={
            "fundamental": 100,
            "valuation": 100,
            "comparables": 100,
            "macro": 100,
            "risk": 100,
        },
        tactical_scores={
            "technical": 100,
            "sentiment": 100,
            "smart_money": 100,
            "macro": 100,
        },
        confidence_inputs={
            "provider_quality": 100,
            "freshness": 100,
            "consistency": 100,
            "completeness": 100,
        },
    )

    assert result.strategic_score == 100
    assert result.tactical_score == 100
    assert result.strategic_decision == "COMPRAR"
    assert result.tactical_decision == "COMPRAR"
    assert result.confidence == 100


def test_neutral_inputs_produce_hold():
    engine = DecisionEngine()
    scores = {"fundamental": 50, "valuation": 50, "comparables": 50, "macro": 50, "risk": 50}
    tactical = {"technical": 50, "sentiment": 50, "smart_money": 50, "macro": 50}
    confidence = {"provider_quality": 80, "freshness": 80, "consistency": 80, "completeness": 80}

    result = engine.evaluate(scores, tactical, confidence)

    assert result.strategic_score == 50
    assert result.tactical_score == 50
    assert result.strategic_decision == "REDUCIR"
    assert result.tactical_decision == "REDUCIR"
