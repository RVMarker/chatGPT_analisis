from types import SimpleNamespace

from investment_analyzer.pipeline.macro_production import ProductionMacroModule


class FakeResponse:
    def __init__(self, payload, text=""):
        self.payload = payload
        self.text = text

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FailingResponse:
    status_code = 400
    text = '{"error":"invalid token 1234567890123456789012345678901234567890"}'

    def raise_for_status(self):
        import requests
        raise requests.HTTPError("400", response=self)


class FakeSession:
    def get(self, url, params=None, headers=None, timeout=None):
        if "stlouisfed.org" in url:
            series = params["series_id"]
            values = {
                "FEDFUNDS": "5.25",
                "CPIAUCSL": "3.10",
                "UNRATE": "4.20",
                "GDPC1": "2.40",
                "DGS10": "4.30",
            }
            return FakeResponse({"observations": [{"date": "2026-07-01", "value": values[series]}]})

        series_ids = url.split("/series/")[1].split("/")[0].split(",")
        values = {
            "SF61745": "7.00",
            "SP30578": "3.37",
            "SF43718": "17.90",
        }
        return FakeResponse(
            {
                "bmx": {
                    "series": [
                        {
                            "idSerie": series_id,
                            "datos": [{"fecha": "07/08/2026", "dato": values[series_id]}],
                        }
                        for series_id in series_ids
                    ]
                }
            }
        )


class FailingBanxicoSession(FakeSession):
    def get(self, url, params=None, headers=None, timeout=None):
        if "banxico.org.mx" in url:
            return FailingResponse()
        return super().get(url, params=params, headers=headers, timeout=timeout)


def test_mexican_asset_gets_us_and_mexico_macro(monkeypatch):
    monkeypatch.setenv("FRED_API_KEY", "test")
    monkeypatch.setenv("BANXICO_TOKEN", "test")
    context = SimpleNamespace(asset=SimpleNamespace(symbol="FMTY14.MX"))
    result = ProductionMacroModule(session=FakeSession()).run(context)

    assert result["available"] is True
    assert result["context_only"] is True
    assert result["score"] is None
    assert result["provider"] == "fred+banxico"
    assert result["us"]["policy_rate"] == 5.25
    assert result["mexico"]["policy_rate"] == 7.0
    assert result["mexico"]["inflation_yoy"] == 3.37
    assert result["mexico"]["usd_mxn"] == 17.90
    assert result["required_margin"] == 30.0


def test_non_mexican_asset_does_not_query_banxico(monkeypatch):
    monkeypatch.setenv("FRED_API_KEY", "test")
    monkeypatch.setenv("BANXICO_TOKEN", "test")
    context = SimpleNamespace(asset=SimpleNamespace(symbol="AAPL"))
    result = ProductionMacroModule(session=FakeSession()).run(context)

    assert result["provider"] == "fred"
    assert result["mexico"] is None
    assert result["us"]["policy_rate"] == 5.25


def test_missing_credentials_keeps_macro_context_safe(monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    monkeypatch.delenv("BANXICO_TOKEN", raising=False)
    context = SimpleNamespace(asset=SimpleNamespace(symbol="FMTY14.MX"))
    result = ProductionMacroModule(session=FakeSession()).run(context)

    assert result["available"] is False
    assert result["us"]["policy_rate"] is None
    assert result["mexico"]["policy_rate"] is None
    assert result["score"] is None


def test_banxico_http_error_is_non_fatal_and_redacts_server_token(monkeypatch):
    monkeypatch.setenv("FRED_API_KEY", "test")
    monkeypatch.setenv("BANXICO_TOKEN", "test")
    context = SimpleNamespace(asset=SimpleNamespace(symbol="FMTY14.MX"))
    result = ProductionMacroModule(session=FailingBanxicoSession()).run(context)

    assert result["available"] is True  # FRED remains available.
    assert result["mexico"]["policy_rate"] is None
    errors = result["diagnostics"]["errors"]
    assert len(errors) == 1
    assert "Banxico batch: HTTPError HTTP 400" in errors[0]
    assert "1234567890123456789012345678901234567890" not in errors[0]
    assert "[REDACTED]" in errors[0]
