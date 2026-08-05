from datetime import datetime, timedelta, timezone

from investment_analyzer.providers.normalizer import ProviderNormalizer


def test_first_value_uses_first_non_null_key():
    assert ProviderNormalizer.first_value({"a": None, "b": 12}, "a", "b") == 12


def test_freshness_decreases_with_age():
    now = datetime.now(timezone.utc)
    assert ProviderNormalizer.freshness(now, now) == 100
    assert ProviderNormalizer.freshness(now - timedelta(days=400), now) == 10


def test_result_is_auditable():
    result = ProviderNormalizer.result("yahoo", {"price": 100}, latency_ms=12.5)
    assert result.provider == "yahoo"
    assert result.success is True
    assert result.payload["price"] == 100
    assert result.latency_ms == 12.5
