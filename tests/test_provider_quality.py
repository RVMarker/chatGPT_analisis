from investment_analyzer.pipeline.provider_quality import score_provider_quality


def test_quality_does_not_depend_on_yahoo_name():
    data = {
        "price": "fmp",
        "financials": "alpha_vantage",
        "history": "twelve_data",
        "price_symbol": "FMty14.MX",
        "financials_symbol": "FMty14.MX",
        "history_symbol": "FMty14.MX",
    }
    assert score_provider_quality(data) == 100.0


def test_empty_provider_or_symbol_is_not_usable():
    data = {
        "price": "fmp",
        "financials": "",
        "history": "twelve_data",
        "price_symbol": "ABC.MX",
        "history_symbol": "",
    }
    assert score_provider_quality(data) == 33.33
