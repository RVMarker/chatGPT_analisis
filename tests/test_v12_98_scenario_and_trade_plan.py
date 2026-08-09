from investment_analyzer.analysis.decision.scenario_adapter import normalize_scenarios
from investment_analyzer.analysis.decision.trade_plan import build_trade_plan


def test_scenarios_are_never_fabricated():
    assert normalize_scenarios({'fair_value': 130}) == {'bear': None, 'base': 130.0, 'bull': None}


def test_trade_plan_blocks_without_real_target1():
    r = build_trade_plan(price=100, fair_value=130, bull_value=150, support=92, resistance=None, capital=5000)
    assert r['operation'] == 'ESPERAR'
    assert r['target_1'] is None
    assert any('Target 1' in x for x in r['reasons'])


def test_trade_plan_uses_real_bull_cap():
    r = build_trade_plan(price=100, fair_value=130, bull_value=120, support=92, resistance=110, capital=5000)
    assert r['target_2'] == 120
