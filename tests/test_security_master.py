"""Tests for Yahoo -> provider symbol translation."""

from pathlib import Path

from investment_analyzer.security.security_master import Security, SecurityMaster
from investment_analyzer.security.symbol_resolver import SymbolResolver


def test_yahoo_symbol_can_map_to_different_provider_symbols(tmp_path: Path):
    db = tmp_path / "security_master.db"
    master = SecurityMaster(str(db))
    master.add(
        Security(
            asset_id="AST-FMTY14",
            canonical_symbol="FMTY14.MX",
            name="Fibra Mty",
            exchange="BMV",
            currency="MXN",
            asset_type="REIT",
            yahoo="FMTY14.MX",
            fmp="FMTY14",
            alpha_vantage="FMTY14.MX",
        )
    )

    resolver = SymbolResolver(master)
    assert resolver.resolve("fmty14.mx") is not None
    assert resolver.provider_symbol("FMTY14.MX", "yahoo") == "FMTY14.MX"
    assert resolver.provider_symbol("FMTY14.MX", "fmp") == "FMTY14"
    assert resolver.provider_symbol("FMTY14.MX", "alpha_vantage") == "FMTY14.MX"
    master.close()


def test_unknown_symbol_is_preserved_for_provider_call(tmp_path: Path):
    master = SecurityMaster(str(tmp_path / "security_master.db"))
    resolver = SymbolResolver(master)
    assert resolver.provider_symbol(" abc ", "fmp") == "ABC"
    master.close()
