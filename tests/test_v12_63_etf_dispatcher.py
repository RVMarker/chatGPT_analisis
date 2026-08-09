from investment_analyzer.analysis.specialized_dispatcher import SpecializedDispatcher


def test_etf_is_connected_and_returns_holdings():
    d=SpecializedDispatcher()
    r=d.analyze('ETF','SPY',{'price':600,'expense_ratio':.0009,'holdings':[{'symbol':'A','weight':10},{'symbol':'B','weight':8}]})
    assert r['asset_type']=='ETF'
    assert r['analysis']['expense_ratio']==.0009
    assert len(r['analysis']['top10'])==2
