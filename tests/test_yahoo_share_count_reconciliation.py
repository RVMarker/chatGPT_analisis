from investment_analyzer.providers.yahoo_adapter import YahooFinanceAdapter


def test_share_count_is_reconciled_when_yahoo_value_is_1000x_too_large():
    normalized, raw, source, scale = YahooFinanceAdapter._reconcile_share_count(
        shares=100_000_000_000,
        market_cap=10_000_000_000,
        current_price=100,
    )

    assert normalized == 100_000_000
    assert raw == 100_000_000_000
    assert source == "yahoo_fast_info_reconciled"
    assert scale == 1000.0


def test_share_count_is_reconciled_when_yahoo_value_is_1000x_too_small():
    normalized, raw, source, scale = YahooFinanceAdapter._reconcile_share_count(
        shares=100_000,
        market_cap=10_000_000_000,
        current_price=100,
    )

    assert normalized == 100_000_000
    assert raw == 100_000
    assert source == "yahoo_fast_info_reconciled"
    assert scale == 0.001


def test_share_count_is_kept_when_difference_is_not_a_clear_scale_error():
    normalized, raw, source, scale = YahooFinanceAdapter._reconcile_share_count(
        shares=95_000_000,
        market_cap=10_000_000_000,
        current_price=100,
    )

    assert normalized == 95_000_000
    assert raw == 95_000_000
    assert source == "yahoo_fast_info"
    assert scale == 1.0


def test_share_count_falls_back_to_market_cap_implied_count_when_missing():
    normalized, raw, source, scale = YahooFinanceAdapter._reconcile_share_count(
        shares=None,
        market_cap=10_000_000_000,
        current_price=100,
    )

    assert normalized == 100_000_000
    assert raw is None
    assert source == "market_cap/current_price"
    assert scale is None
