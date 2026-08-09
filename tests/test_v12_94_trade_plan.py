from investment_analyzer.analysis.decision.trade_plan import TradePlanEngine


def test_trade_plan_calculates_sl_targets_rr_and_position():
    r=TradePlanEngine().build(price=100,fair_value=130,bear_value=104,bull_value=156,support=92,resistance=115,capital=5000,risk_pct=.02,max_position_pct=.25,min_rr=2)
    assert r['operation']=='COMPRAR'
    assert r['stop_loss']==92
    assert r['target_1']==115
    assert r['target_2']==130
    assert round(r['margin_of_safety_pct'],2)==23.08
    assert round(r['risk_reward'],2)==3.75
    assert r['units']==12
    assert r['position_value']==1200
    assert r['actual_risk']==96


def test_quality_gate_blocks_bad_rr_and_low_margin():
    r=TradePlanEngine().build(price=125,fair_value=130,bull_value=150,support=120,resistance=128,capital=5000,risk_pct=.02,min_rr=2,min_mos_pct=10)
    assert r['operation']=='ESPERAR'
    assert any('Margin of Safety' in x for x in r['reasons'])
