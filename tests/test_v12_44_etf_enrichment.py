from investment_analyzer.analysis.etf_enrichment import ETFEnricher


def test_enricher_uses_first_available_provider_and_tracks_source():
    r=ETFEnricher().enrich({"yahoo":{"totalAssets":100},"fmp":{"expenseRatio":0.001,"benchmark":"S&P 500","holdings":[{"symbol":"A","weight":7}]}})
    assert r.expense_ratio==0.001
    assert r.benchmark=="S&P 500"
    assert r.aum==100
    assert r.holdings[0]["symbol"]=="A"
    assert r.source_map["expense_ratio"]=="fmp"


def test_missing_fields_are_explicit():
    r=ETFEnricher().enrich({"yahoo":{"totalAssets":100}})
    assert r.expense_ratio is None
    assert r.holdings==[]
    assert r.warnings
