from investment_analyzer.analysis.decision_quality_gate import DecisionQualityGate


def test_good_entry_is_buy():
    r=DecisionQualityGate().evaluate(strategic_verdict='COMPRAR',tactical_verdict='COMPRAR',score=80,fair_value=130,price=100,risk_reward=3.0,margin_of_safety=.30,data_coverage=95)
    assert r['operation']=='COMPRAR'


def test_bad_risk_reward_waits():
    r=DecisionQualityGate().evaluate(strategic_verdict='COMPRAR',tactical_verdict='COMPRAR',score=80,fair_value=130,price=100,risk_reward=1.2,margin_of_safety=.30,data_coverage=95)
    assert r['operation']=='ESPERAR'


def test_expensive_asset_waits():
    r=DecisionQualityGate().evaluate(strategic_verdict='COMPRAR',tactical_verdict='COMPRAR',score=80,fair_value=105,price=100,risk_reward=3,margin_of_safety=.05,data_coverage=95)
    assert r['operation']=='ESPERAR'
