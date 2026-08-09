from investment_analyzer.analysis.position_sizing import PositionSizer


def test_position_size_respects_two_percent_risk():
    r=PositionSizer().calculate(capital=5000,entry=100,stop_loss=92,risk_pct=.02)
    assert r['risk_budget']==100
    assert r['units']==12
    assert r['position_value']==1200
    assert r['actual_risk']==96


def test_position_size_respects_max_position_cap():
    r=PositionSizer().calculate(capital=5000,entry=100,stop_loss=50,risk_pct=.02,max_position_pct=.10)
    assert r['units']==5
    assert r['position_value']==500
