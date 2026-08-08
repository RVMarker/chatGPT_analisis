from types import SimpleNamespace
from investment_analyzer.pipeline.actionable_decision import ActionableDecisionAdapter


def test_adapter_creates_strategic_and_tactical_actions():
    result=SimpleNamespace(
        strategic={"verdict":"VENDER","score":20},
        tactical={"verdict":"MANTENER","score":51},
        confidence=95, data_coverage=100,
    )
    ActionableDecisionAdapter().apply(result)
    assert result.actionable["strategic"]["verdict"] == "VENDER"
    assert result.actionable["tactical"]["verdict"] == "MANTENER"
    assert result.actionable["strategic"]["robustness"] == "ALTA"
