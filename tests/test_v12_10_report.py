from types import SimpleNamespace
from investment_analyzer.pipeline.actionable_decision import ActionableDecisionAdapter
from investment_analyzer.reporting.decision_report import decision_to_dict, render_cli, render_json


def test_report_serializes_native_decision_result():
    result=SimpleNamespace(strategic_score=23.7,tactical_score=51.0,strategic_decision="VENDER",tactical_decision="MANTENER",confidence=95.1,data_coverage=100.0,strategic_coverage=100.0,tactical_coverage=100.0,decisive_factors=["valuation presiona a la baja"],missing_factors=[],actionable={})
    ActionableDecisionAdapter().apply(result)
    d=decision_to_dict(result)
    assert d["schema_version"] == "12.10"
    assert d["decision_summary"]["strategic"]["verdict"] == "VENDER"
    assert "VENDER" in render_cli(result)
    assert '"schema_version": "12.10"' in render_json(result)
