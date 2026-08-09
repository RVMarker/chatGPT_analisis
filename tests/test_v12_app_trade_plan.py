from types import SimpleNamespace

from investment_analyzer.app import attach_trade_plan


def test_attach_trade_plan_uses_real_values_and_user_capital():
    context = SimpleNamespace(
        price=SimpleNamespace(current=100.0),
        valuation={"fair_value_per_share": 140.0, "bull_case": 160.0},
        technical={"support": 90.0, "resistance": 115.0},
    )
    plan = attach_trade_plan(context, capital=5000, risk_pct=.02, max_position_pct=.25)
    assert plan["entry"] == 100.0
    assert plan["stop_loss"] == 90.0
    assert plan["target_1"] == 115.0
    assert plan["target_2"] == 140.0
    assert plan["units"] == 10
    assert plan["actual_risk"] == 100
