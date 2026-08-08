from investment_analyzer.analysis.decision.decision_engine import DecisionEngine


def _inputs(valuation_quality):
    return {
        "provider_quality": 100,
        "freshness": 100,
        "consistency": 100,
        "completeness": 100,
        "valuation_quality": valuation_quality,
    }


def test_valuation_quality_reduces_confidence_without_changing_decision_score():
    engine = DecisionEngine()
    high = engine.evaluate(
        strategic_scores={"fundamental": 70, "valuation": 70, "risk": 70},
        tactical_scores={"technical": 70, "sentiment": 70, "smart_money": 70},
        confidence_inputs=_inputs("HIGH"),
    )
    medium = engine.evaluate(
        strategic_scores={"fundamental": 70, "valuation": 70, "risk": 70},
        tactical_scores={"technical": 70, "sentiment": 70, "smart_money": 70},
        confidence_inputs=_inputs("MEDIUM"),
    )

    assert high.strategic_score == medium.strategic_score == 70
    assert high.tactical_score == medium.tactical_score == 70
    assert high.strategic_decision == medium.strategic_decision == "ACUMULAR"
    assert high.tactical_decision == medium.tactical_decision == "ACUMULAR"
    assert high.confidence == 100
    assert medium.confidence == 97.5
    assert any("Calidad de valoración MEDIUM" in flag for flag in medium.red_flags)


def test_valuation_quality_defaults_to_full_confidence_for_legacy_callers():
    result = DecisionEngine().evaluate(
        strategic_scores={"fundamental": 100, "valuation": 100, "risk": 100},
        tactical_scores={"technical": 100, "sentiment": 100, "smart_money": 100},
        confidence_inputs={
            "provider_quality": 100,
            "freshness": 100,
            "consistency": 100,
            "completeness": 100,
        },
    )
    assert result.confidence == 100
