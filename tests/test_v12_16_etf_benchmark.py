from investment_analyzer.analysis.valuation.etf_engine import ETFValuationEngine


def test_etf_benchmark_tracking_and_distribution():
    r=ETFValuationEngine().calculate(
        holdings=[{"ticker":"A","weight_pct":30}], expense_ratio=.15,
        benchmark="S&P 500", category="US Large Cap", benchmark_return=10,
        etf_return=9, tracking_difference=.20, tracking_error=.30,
        dividend_yield=1.4, distribution_frequency="TRIMESTRAL",
    )
    assert r.benchmark == "S&P 500"
    assert r.category == "US Large Cap"
    assert r.relative_return_pct == -1
    assert r.dividend_yield_pct == 1.4
    assert r.distribution_frequency == "TRIMESTRAL"
    assert r.tracking_error_pct == .30
    assert r.quality_score is not None
