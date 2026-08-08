from types import SimpleNamespace

from investment_analyzer.pipeline.macro_production import ProductionMacroModule


class EmptySession:
    def get(self, *args, **kwargs):
        raise AssertionError("network should not be called without credentials")


def test_macro_without_credentials_is_unavailable_even_if_dotenv_exists(monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    monkeypatch.delenv("FRED_KEY", raising=False)
    monkeypatch.delenv("BANXICO_TOKEN", raising=False)
    monkeypatch.delenv("BANXICO_KEY", raising=False)
    monkeypatch.delenv("BMX_TOKEN", raising=False)
    monkeypatch.delenv("BANXICO_API_KEY", raising=False)

    result = ProductionMacroModule(session=EmptySession()).run(
        SimpleNamespace(asset=SimpleNamespace(symbol="FMTY14.MX"))
    )

    assert result["available"] is False
    assert result["diagnostics"]["fred_configured"] is False
    assert result["diagnostics"]["banxico_configured"] is False
    assert result["diagnostics"]["fred_observations"] == 0
    assert result["diagnostics"]["mexico_observations"] == 0
