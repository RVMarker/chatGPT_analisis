from investment_analyzer.analysis.decision.decision_engine import DecisionEngine


def test_actionable_decision_exposes_decisive_and_missing_factors():
    result = DecisionEngine().evaluate(
        strategic_scores={"fundamental": 30, "valuation": 10, "risk": 35},
        tactical_scores={"technical": 55, "sentiment": 50, "smart_money": 60},
        confidence_inputs={
            "provider_quality": 95,
            "freshness": 95,
            "consistency": 90,
            "completeness": 95,
            "technical_data_quality": 90,
            "valuation_quality": "LOW_MEDIUM",
        },
        contextual={"comparables": 80, "macro": 60},
    )
    assert result.strategic_decision == "VENDER"
    assert result.decisive_factors
    assert result.contextual_factors == [
        "comparables: contexto; no vota directamente",
        "macro: contexto; no vota directamente",
    ]
    assert any("Calidad valoración: LOW_MEDIUM" in x for x in result.missing_factors)


def test_missing_decision_component_does_not_get_fake_neutral_score():
    result = DecisionEngine().evaluate(
        strategic_scores={"fundamental": 80, "valuation": None, "risk": 80},
        tactical_scores={"technical": 70, "sentiment": 70, "smart_money": 70},
        confidence_inputs={},
    )
    valuation = next(x for x in result.strategic_breakdown if x.name == "valuation")
    assert valuation.score is None
    assert valuation.available is False
    assert valuation.weighted == 0
    assert result.strategic_coverage < 100
