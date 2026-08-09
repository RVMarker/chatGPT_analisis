import pytest

from investment_analyzer.analysis.decision.decision_engine import DecisionEngine


def test_consolidated_decision_engine_uses_v12_weights():
    engine = DecisionEngine()
    score, coverage_items, _ = engine.strategic({
        "fundamental": 80,
        "valuation": 70,
        "technical": 60,
        "risk": 50,
    })
    assert score == pytest.approx(68.5)
    assert all(item.available for item in coverage_items)


def test_missing_component_is_excluded_and_not_replaced_by_50():
    engine = DecisionEngine()
    score, items, _ = engine.strategic({
        "fundamental": 80,
        "valuation": None,
        "technical": 60,
        "risk": 50,
    })
    assert score == pytest.approx(67.86)
    assert items[1].available is False
    assert items[1].weight == 0.0
