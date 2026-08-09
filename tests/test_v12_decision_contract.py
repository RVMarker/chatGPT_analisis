from investment_analyzer.analysis.decision.decision_engine import DecisionEngine
from investment_analyzer.analysis.decision.decision_weights import STRATEGIC, TACTICAL


def test_v12_weights_are_explicit():
    assert STRATEGIC == {"fundamental": 0.35, "valuation": 0.30, "technical": 0.20, "risk": 0.15}
    assert TACTICAL == {"technical": 0.45, "sentiment": 0.30, "smart_money": 0.25}


def test_missing_confidence_inputs_do_not_crash_or_become_80():
    value = DecisionEngine.confidence(100, None, None, 100, 100, 100, None)
    assert value == 60.0


def test_strategic_score_uses_technical():
    engine = DecisionEngine()
    score, items, _ = engine.strategic({
        "fundamental": 80,
        "valuation": 70,
        "technical": 60,
        "risk": 50,
    })
    assert score == 68.5
    assert [item.name for item in items] == ["fundamental", "valuation", "technical", "risk"]
