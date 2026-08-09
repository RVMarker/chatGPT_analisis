from orchestrator import build_parser, parse_provider_symbols
from investment_analyzer.providers.provider_registry import ProviderRegistry


def test_registry_defaults_registers_yahoo():
    registry=ProviderRegistry().register_defaults(yahoo_provider=lambda symbol:{"price":1})
    assert registry.exists("yahoo")
    assert "yahoo" in registry.fetchers()


def test_cli_provider_symbol_mapping():
    assert parse_provider_symbols(["yahoo=FMTY14.MX"]) == {"yahoo":"FMTY14.MX"}
    assert build_parser().parse_args(["--once"]).once is True
