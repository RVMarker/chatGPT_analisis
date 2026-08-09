from types import SimpleNamespace
from investment_analyzer.report.multi_asset_report import MultiAssetReport


def test_fibra_report_uses_fibra_metrics():
    c=SimpleNamespace(asset=SimpleNamespace(symbol='FMTY14.MX'),metadata={'asset_classification':{'asset_type':'FIBRA','confidence':100},'specialized_analysis':{'analysis':{'strategic_score':23.7,'tactical_score':51,'strategic_coverage':100,'tactical_coverage':100,'ffo_share':.4541,'affo_share':None,'nav_share':None,'distribution_share':None}}},comparables={},macro={})
    text=MultiAssetReport().render(c)
    assert 'REIT / FIBRA' in text and 'FFO/share' in text


def test_stock_report_uses_stock_metrics():
    c=SimpleNamespace(asset=SimpleNamespace(symbol='AAPL'),metadata={'asset_classification':{'asset_type':'STOCK'},'specialized_analysis':{'analysis':{'strategic_score':70,'tactical_score':60,'strategic_coverage':100,'tactical_coverage':100,'fair_value':220,'margin_of_safety':10}}},comparables={},macro={})
    text=MultiAssetReport().render(c)
    assert 'ACCIÓN — VALORACIÓN' in text and 'Fair value: 220' in text
