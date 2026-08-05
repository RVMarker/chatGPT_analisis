from investment_analyzer.security.asset_loader import AssetLoader
from investment_analyzer.security.security_master import Security, SecurityMaster


def test_unknown_symbol_remains_canonical_yahoo_symbol(tmp_path):
    master = SecurityMaster(str(tmp_path / "security.db"))
    asset = AssetLoader(master).load(" fmty14.mx ")
    assert asset.symbol == "FMTY14.MX"
    assert asset.identifiers.yahoo == "FMTY14.MX"
    assert asset.identifiers.fmp is None
    master.close()


def test_security_master_maps_provider_symbols_without_changing_asset_symbol(tmp_path):
    master = SecurityMaster(str(tmp_path / "security.db"))
    master.add(Security(
        asset_id="AST-FMTY14", canonical_symbol="FMTY14.MX", name="Fibra Mty",
        exchange="BMV", currency="MXN", asset_type="REIT", yahoo="FMTY14.MX",
        fmp="FMTY14", polygon="FMTY14:BMV",
    ))
    asset = AssetLoader(master).load("FMTY14.MX")
    assert asset.symbol == "FMTY14.MX"
    assert asset.identifiers.yahoo == "FMTY14.MX"
    assert asset.identifiers.fmp == "FMTY14"
    assert asset.identifiers.polygon == "FMTY14:BMV"
    assert master.provider_symbol("FMTY14.MX", "fmp") == "FMTY14"
    master.close()
