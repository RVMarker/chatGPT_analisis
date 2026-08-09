from investment_analyzer.analysis.reit_fibra_analyzer import REITFibraAnalyzer
from investment_analyzer.analysis.specialized_dispatcher import SpecializedDispatcher


def test_reit_fibra_core_metrics():
    r=REITFibraAnalyzer().analyze('FMTY14.MX',{'price':14.0,'ffo_share':.7,'affo_share':.6,'nav_share':16.0,'distribution_share':.5,'debt_ebitda':5.2,'interest_coverage':2.8,'occupancy':.95,'wale':4.2,'cap_rate':.08})
    assert round(r['ffo_multiple'],2)==20.0
    assert round(r['affo_multiple'],2)==23.33
    assert round(r['nav_premium_discount'],2)==-12.5
    assert round(r['payout_on_affo'],2)==83.33
    assert round(r['distribution_yield'],2)==3.57


def test_dispatcher_uses_reit_fibra_analyzer():
    r=SpecializedDispatcher().analyze('FIBRA','FMTY14.MX',{'price':14,'ffo_share':.7,'nav_share':16})
    assert r['asset_type']=='FIBRA'
    assert r['analysis']['ffo_share']==.7
