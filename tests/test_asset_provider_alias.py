from investment_analyzer.security.asset_loader import AssetLoader
from investment_analyzer.security.security_master import SecurityMaster


def test_fmp_style_symbol_resolves_to_canonical_yahoo_symbol(tmp_path):
    master = SecurityMaster(str(tmp_path / "security_master.db"))
    master.seed_production_defaults()
    asset = AssetLoader(master).load("fmty14")
    assert asset.symbol == "FMTY14.MX"
    assert asset.identifiers.yahoo == "FMTY14.MX"
    assert asset.identifiers.fmp == "FMTY14"
    master.close()
