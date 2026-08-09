from investment_analyzer.analysis.decision.valuation_scenarios import ValuationScenarioEngine


def test_builds_bear_base_bull_and_margin():
    r=ValuationScenarioEngine().build({'price':100,'fair_value':130})
    assert r['bear_value']==104
    assert r['base_fair_value']==130
    assert r['bull_value']==156
    assert r['margin_of_safety_pct']==23.08


def test_averages_available_valuation_methods_without_defaults():
    r=ValuationScenarioEngine().build({'price':100,'dcf_fair_value':120,'graham_value':140})
    assert r['base_fair_value']==130
    assert r['bear_value']==104
    assert r['bull_value']==156
