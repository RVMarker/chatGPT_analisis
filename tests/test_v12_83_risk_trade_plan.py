from investment_analyzer.analysis.risk_trade_plan import RiskTradePlan


def test_trade_plan_uses_support_and_fair_value():
    r=RiskTradePlan().build(price=100,fair_value=130,technical_support=92,technical_resistance=115)
    assert r['stop_loss']==92
    assert r['target_1']==115
    assert r['target_2']==130
    assert r['risk_reward']==3.75


def test_trade_plan_uses_atr_when_support_missing():
    r=RiskTradePlan().build(price=100,atr=4)
    assert r['stop_loss']==92
    assert r['target_1'] is not None
    assert r['risk_reward'] is not None
