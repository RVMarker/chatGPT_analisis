from types import SimpleNamespace

from investment_analyzer.pipeline.macro_production import ProductionMacroModule


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeSession:
    def get(self, url, params=None, headers=None, timeout=None):
        if "stlouisfed.org" in url:
            return FakeResponse({"observations": [{"date": "2026-07-01", "value": "5.25"}]})
        return FakeResponse(
            {
                "bmx": {
                    "series": [
                        {"idSerie": "SF61745", "datos": [{"fecha": "07/08/2026", "dato": "7.00"}]},
                        {"idSerie": "SP30578", "datos": [{"fecha": "07/08/2026", "dato": "3.12"}]},
                        {"idSerie": "SF43718", "datos": [{"fecha": "07/08/2026", "dato": "17.14"}]},
                    ]
                }
            }
        )


def test_macro_reports_configuration_and_source_errors(monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    monkeypatch.delenv("FRED_KEY", raising=False)
    monkeypatch.delenv("BANXICO_TOKEN", raising=False)
    monkeypatch.delenv("BMX_TOKEN", raising=False)
    monkeypatch.delenv("BANXICO_API_KEY", raising=False)

    result = ProductionMacroModule(session=FakeSession()).run(
        SimpleNamespace(asset=SimpleNamespace(symbol="FMTY14.MX"))
    )

    assert result["available"] is False
    assert result["diagnostics"]["fred_configured"] is False
    assert result["diagnostics"]["banxico_configured"] is False
    assert result["diagnostics"]["fred_observations"] == 0
    assert result["diagnostics"]["mexico_observations"] == 0


def test_macro_diagnostics_count_available_observations(monkeypatch):
    monkeypatch.setenv("FRED_API_KEY", "test")
    monkeypatch.setenv("BANXICO_TOKEN", "test")

    result = ProductionMacroModule(session=FakeSession()).run(
        SimpleNamespace(asset=SimpleNamespace(symbol="FMTY14.MX"))
    )

    assert result["diagnostics"]["fred_configured"] is True
    assert result["diagnostics"]["banxico_configured"] is True
    assert result["diagnostics"]["fred_observations"] == 5
    assert result["diagnostics"]["mexico_observations"] == 4
    assert result["diagnostics"]["errors"] == []
