from investment_analyzer.analysis.risk_trade_plan import RiskTradePlan


def test_target_two_is_capped_by_bull_case():
    r=RiskTradePlan().build(price=100,fair_value=130,bear_value=104,bull_value=120,technical_support=92,technical_resistance=115)
    assert r['target_2']==120
    assert r['target_1']==115
    assert r['risk_reward']==2.5


def test_target_two_uses_fair_value_when_bull_is_higher():
    r=RiskTradePlan().build(price=100,fair_value=130,bull_value=156,technical_support=92,technical_resistance=115)
    assert r['target_2']==130
    assert r['risk_reward']==3.75
