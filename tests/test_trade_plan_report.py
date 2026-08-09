from investment_analyzer.pipeline.trade_plan_report import render_trade_plan


def test_trade_plan_report_contains_operational_levels():
    text = render_trade_plan({
        "operation": "COMPRAR",
        "entry": 100.0,
        "stop_loss": 92.0,
        "target_1": 115.0,
        "target_2": 130.0,
        "margin_of_safety_pct": 23.08,
        "risk_reward": 3.75,
        "units": 10,
        "position_value": 1000.0,
        "risk_budget": 100.0,
        "actual_risk": 80.0,
    })
    assert "Entry" in text
    assert "Stop Loss" in text
    assert "Target 1" in text
    assert "Target 2" in text
    assert "R/R" in text
    assert "Riesgo real" in text
