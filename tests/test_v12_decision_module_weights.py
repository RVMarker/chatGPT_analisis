from types import SimpleNamespace

from investment_analyzer.pipeline.decision_module import DecisionModule


def test_strategic_uses_all_four_components():
    context = SimpleNamespace(
        fundamentals={"score": 80},
        valuation={"score": 70},
        technical={"score": 60, "available": True},
        risk={"score": 50},
        sentiment={"score": 80},
        comparables={"score": 90},
        macro={"score": 90},
        metadata={
            "smart_money": {"score": 80},
            "data_providers": {"price": "yahoo", "financials": "yahoo", "history": "yahoo"},
        },
        technical_result={"available": True, "requirements": {"a": True}},
        decision=None,
    )
    result = DecisionModule().run(context)
    assert result.strategic_score == 68.5
    assert result.strategic_coverage == 100.0
    weights = {x.name: x.weight for x in result.strategic_breakdown}
    assert weights == {"fundamental": .35, "valuation": .30, "technical": .20, "risk": .15}
