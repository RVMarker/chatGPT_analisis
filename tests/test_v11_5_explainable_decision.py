from investment_analyzer.analysis.decision.decision_engine import DecisionEngine


def test_decision_result_contains_auditable_trail_and_context_separation():
    result = DecisionEngine().evaluate(
        strategic_scores={"fundamental": 33.0, "valuation": 10.0, "risk": 32.0},
        tactical_scores={"technical": 32.0, "sentiment": 80.0, "smart_money": 58.0},
        confidence_inputs={
            "provider_quality": 95,
            "freshness": 100,
            "consistency": 80,
            "completeness": 100,
            "technical_data_quality": 100,
            "valuation_quality": "LOW_MEDIUM",
        },
        contextual={"comparables": 20.0, "macro": 70.0},
    )

    assert result.strategic_decision == "VENDER"
    assert result.tactical_decision == "MANTENER"
    assert len(result.decision_trail) == 6
    assert all(item["role"] == "VOTE" for item in result.decision_trail)
    assert "comparables" in result.contextual
    assert "macro" in result.contextual
    assert all("no vota directamente" in text for text in result.contextual_factors)
    assert any("valuation" in text.lower() for text in result.decisive_factors)
    assert any("Calidad valoración" in text for text in result.missing_factors)


def test_missing_vote_does_not_become_neutral_score():
    result = DecisionEngine().evaluate(
        strategic_scores={"fundamental": 20.0, "valuation": None, "risk": 30.0},
        tactical_scores={"technical": 60.0, "sentiment": 60.0, "smart_money": 60.0},
        confidence_inputs={},
    )

    valuation = next(x for x in result.strategic_breakdown if x.name == "valuation")
    assert valuation.score is None
    assert valuation.available is False
    assert valuation.weighted == 0.0
    assert result.strategic_coverage == 66.67
