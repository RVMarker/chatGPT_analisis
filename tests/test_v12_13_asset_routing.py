from investment_analyzer.analysis.integration.fundamental_valuation_risk import FinancialAnalysisIntegrator


def test_asset_aliases_cover_required_universe():
    i=FinancialAnalysisIntegrator()
    assert i.normalize_asset_type("stocks")=="STOCK"
    assert i.normalize_asset_type("etfs")=="ETF"
    assert i.normalize_asset_type("reits")=="REIT"
    assert i.normalize_asset_type("fibras")=="FIBRA"
    assert i.normalize_asset_type("crypto")=="CRYPTO"
    assert i.normalize_asset_type("bonds")=="BOND"


def test_unknown_asset_is_rejected():
    try: FinancialAnalysisIntegrator().normalize_asset_type("OPTION")
    except ValueError as exc: assert "no soportada" in str(exc)
    else: raise AssertionError("Unsupported asset type was accepted")
