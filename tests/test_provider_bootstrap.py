from investment_analyzer.providers.provider_bootstrap import build_provider_stack


class FakeYahoo:
    NAME = "yahoo"


def test_bootstrap_registers_yahoo_in_both_layers():
    registry, manager = build_provider_stack(FakeYahoo())
    assert registry.exists("YAHOO")
    assert registry.get("yahoo") is not None
    assert "yahoo" in manager.providers
    assert manager.providers["yahoo"].priority == 10
