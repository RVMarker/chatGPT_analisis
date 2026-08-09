from investment_analyzer.analysis.decision_quality_gate import DecisionQualityGate


def test_buy_requires_complete_trade_plan():
    g=DecisionQualityGate()
    r=g.evaluate(strategic_verdict='COMPRAR',tactical_verdict='COMPRAR',score=80,fair_value=130,price=100,risk_reward=None,margin_of_safety=.30)
    assert r['operation']=='ESPERAR'
    assert any('R/R no disponible' in x for x in r['reasons'])


def test_buy_passes_only_with_executable_plan():
    g=DecisionQualityGate()
    r=g.evaluate(strategic_verdict='COMPRAR',tactical_verdict='COMPRAR',score=80,fair_value=130,price=100,risk_reward=3.0,margin_of_safety=.30,stop_loss=92,target_1=115,target_2=130,data_coverage=90)
    assert r['operation']=='COMPRAR'
