from orchestrator import _weighted


def test_strategic_weights_are_35_30_20_15():
    score, coverage, breakdown = _weighted(
        {"fundamental": {"score": 80}, "valuation": {"score": 70}, "technical": {"score": 60}, "risk": {"score": 50}},
        {"fundamental": .35, "valuation": .30, "technical": .20, "risk": .15},
    )
    assert score == 68.5
    assert coverage == 100.0
    assert breakdown["fundamental"]["weight"] == .35


def test_missing_component_is_not_replaced_by_50():
    score, coverage, _ = _weighted(
        {"fundamental": {"score": 80}, "valuation": {"score": None}, "technical": {"score": 60}, "risk": {"score": 50}},
        {"fundamental": .35, "valuation": .30, "technical": .20, "risk": .15},
    )
    assert coverage == 75.0
    assert round(score, 2) == round((80*.35 + 60*.20 + 50*.15)/.70, 2)
