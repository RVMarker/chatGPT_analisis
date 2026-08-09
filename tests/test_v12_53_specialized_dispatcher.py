from investment_analyzer.analysis.specialized_dispatcher import SpecializedDispatcher


def test_dispatcher_normalizes_all_six_asset_families():
    d=SpecializedDispatcher()
    assert d.normalize('equity')=='STOCK'
    assert d.normalize('ETF')=='ETF'
    assert d.normalize('fibra')=='FIBRA'
    assert d.normalize('crypto')=='CRYPTO'
    assert d.normalize('bono')=='BOND'
    assert d.normalize('fixed-income')=='BOND'


def test_dispatcher_routes_stock():
    r=SpecializedDispatcher().analyze('equity','ABC',{'price':100,'dcf_value':120})
    assert r['asset_type']=='STOCK'
    assert r['analysis']['fair_value']==120
