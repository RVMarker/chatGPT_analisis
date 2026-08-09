from investment_analyzer.analysis.decision.final_decision import finalize_decision


def test_buy_thesis_requires_approved_trade_plan():
    assert finalize_decision("COMPRAR", {"operation": "COMPRAR"})["decision"] == "COMPRAR"
    assert finalize_decision("COMPRAR", {"operation": "ESPERAR", "reasons": ["R/R insuficiente"]})["decision"] == "ESPERAR"


def test_negative_thesis_overrides_trade_plan():
    assert finalize_decision("VENDER", {"operation": "COMPRAR"})["decision"] == "VENDER"
    assert finalize_decision("REDUCIR", {"operation": "COMPRAR"})["decision"] == "REDUCIR"


def test_hold_does_not_create_new_entry():
    assert finalize_decision("MANTENER", {"operation": "COMPRAR"})["decision"] == "MANTENER"
