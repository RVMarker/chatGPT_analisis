from investment_analyzer.analysis.decision.trade_plan import build_trade_plan


def test_missing_support_and_atr_blocks_trade():
    r = build_trade_plan(price=100, fair_value=130, bull_value=150, resistance=120)
    assert r['operation'] == 'ESPERAR'
    assert r['stop_loss'] is None


def test_target_two_is_capped_by_bull_case():
    r = build_trade_plan(price=100, fair_value=130, bull_value=120, support=90, resistance=110)
    assert r['target_2'] == 120


def test_position_size_respects_risk_budget():
    r = build_trade_plan(price=100, fair_value=140, bull_value=160, support=90,
                         resistance=115, capital=5000, risk_pct=.02,
                         max_position_pct=.25)
    assert r['units'] == 10
    assert r['actual_risk'] == 100
