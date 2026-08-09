from investment_analyzer.providers.provider_bootstrap import build_provider_stack
from investment_analyzer.security.security_master import SecurityMaster


def test_security_master_mapping_is_used_by_provider_manager(tmp_path):
    master = SecurityMaster(str(tmp_path / "security_master.db"))
    master.add(__import__("investment_analyzer.security.security_master", fromlist=["Security"]).Security(
        asset_id="AST-FMTY14",
        canonical_symbol="FMTY14.MX",
        name="Fibra Mty",
        exchange="BMV",
        currency="MXN",
        asset_type="REIT",
        yahoo="FMTY14.MX",
        fmp="FMTY14",
    ))
    _, manager = build_provider_stack(security_master=master)
    assert manager.provider_symbol("FMTY14.MX", "yahoo") == "FMTY14.MX"
    assert manager.provider_symbol("FMTY14.MX", "fmp") == "FMTY14"
    master.close()
