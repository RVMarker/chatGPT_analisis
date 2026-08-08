import pytest
from investment_analyzer.analysis.asset_classification import get_asset_policy, normalize_asset_type
from investment_analyzer.common.enums import AssetType

@pytest.mark.parametrize("raw,expected",[("stock",AssetType.STOCK),("ETF",AssetType.ETF),("REIT",AssetType.REIT),("FIBRA",AssetType.FIBRA),("crypto",AssetType.CRYPTO),("bond",AssetType.BOND),("bonds",AssetType.BOND),("fibras",AssetType.FIBRA)])
def test_all_core_asset_types_normalize(raw,expected):
    assert normalize_asset_type(raw) is expected

@pytest.mark.parametrize("asset,model",[(AssetType.STOCK,"DCF"),(AssetType.ETF,"ETF_RELATIVE_NAV"),(AssetType.REIT,"FFO_CAPITALIZATION"),(AssetType.FIBRA,"FFO_CAPITALIZATION"),(AssetType.CRYPTO,"CRYPTO_NETWORK_MARKET"),(AssetType.BOND,"BOND_YIELD_DURATION")])
def test_every_core_asset_has_explicit_valuation_policy(asset,model):
    p=get_asset_policy(asset)
    assert p.valuation_model==model
    assert p.strategic_modules
    assert p.tactical_modules
    assert p.required_fields


def test_unknown_asset_is_rejected():
    with pytest.raises(ValueError): normalize_asset_type("OPTION")
