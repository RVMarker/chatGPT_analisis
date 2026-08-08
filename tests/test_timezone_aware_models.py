from datetime import timezone

from investment_analyzer.common.models import PriceData


def test_price_data_default_timestamp_is_timezone_aware_utc():
    timestamp = PriceData(symbol="FMTY14.MX", current=10.0).timestamp
    assert timestamp.tzinfo is timezone.utc
