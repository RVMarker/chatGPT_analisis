from types import SimpleNamespace
from investment_analyzer.reporting.decision_report import decision_to_dict, render_cli, render_json


def result():
    return SimpleNamespace(
        strategic_score=23.7, tactical_score=51.0,
        strategic_decision="VENDER", tactical_decision="MANTENER",
        confidence=95.1, data_coverage=100.0,
        strategic_coverage=100.0, tactical_coverage=100.0,
        actionable={
            "strategic":{"action":"CONSIDERAR REDUCCIÓN / SALIDA SEGÚN MANDATO","robustness":"ALTA","severity":"ALTA","rationale":"score=23.7"},
            "tactical":{"action":"MANTENER / MONITOREAR TESIS","robustness":"ALTA","severity":"BAJA","rationale":"score=51.0"},
        }, decisive_factors=["valuation presiona a la baja (10.0/100)"], missing_factors=[],
    )


def test_report_contains_both_horizons_and_actions():
    text=render_cli(result())
    assert "DECISIÓN ESTRATÉGICA" in text
    assert "DECISIÓN TÁCTICA" in text
    assert "CONSIDERAR REDUCCIÓN" in text
    assert "MANTENER / MONITOREAR" in text


def test_json_is_versioned_and_structured():
    data=decision_to_dict(result())
    assert data["schema_version"] == "12.10"
    assert data["decision_summary"]["strategic"]["verdict"] == "VENDER"
    assert "actionable" in data
    assert '"schema_version"' in render_json(result())
