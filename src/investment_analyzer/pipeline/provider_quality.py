"""Provider quality scoring independent of provider brand/name."""
from __future__ import annotations


def score_provider_quality(data_providers: dict | None) -> float:
    """Score availability of price, financials and history sources.

    Quality measures whether usable provider data exists, not whether it came
    from Yahoo. Provider names remain metadata only. A source counts when a
    non-empty provider identifier is present and the corresponding symbol is
    also present when that symbol field exists.
    """
    data = data_providers or {}
    groups = ("price", "financials", "history")
    available = 0
    for group in groups:
        provider = data.get(group)
        if not provider:
            continue
        symbol = data.get(f"{group}_symbol")
        if symbol is not None and not str(symbol).strip():
            continue
        available += 1
    return round(100.0 * available / len(groups), 2)
