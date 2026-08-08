from investment_analyzer.analysis.decision.action_policy import ActionPolicyEngine


def test_sell_high_confidence_is_actionable():
    p=ActionPolicyEngine().evaluate("VENDER",20,95,100)
    assert p.robustness=="ALTA"
    assert p.severity=="ALTA"
    assert "REDUCCIÓN" in p.action


def test_low_confidence_never_becomes_aggressive_action():
    p=ActionPolicyEngine().evaluate("VENDER",20,40,50)
    assert p.robustness=="BAJA"
    assert "NO AUMENTAR" in p.action
