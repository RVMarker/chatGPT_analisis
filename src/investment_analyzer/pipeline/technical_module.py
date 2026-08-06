"""Technical stage for the V11 pipeline.

The current PriceData contract contains a single OHLC snapshot, not a price
history. Therefore this module deliberately does not fabricate RSI/MACD/SMA
values. It scores only what can be supported by the available snapshot and
reports the missing history explicitly.
"""
from __future__ import annotations

from math import isfinite


class TechnicalModule:
    def run(self, context):
        price = context.price
        if price is None:
            return {"score": 50.0, "available": False, "reason": "Sin PriceData"}

        current = _num(getattr(price, "current", None))
        previous = _num(getattr(price, "previous_close", None))
        high = _num(getattr(price, "high", None))
        low = _num(getattr(price, "low", None))

        score = 50.0
        evidence = []

        if current is not None and previous is not None and previous > 0:
            change_pct = (current / previous - 1.0) * 100.0
            # Snapshot momentum: bounded contribution, never a substitute for RSI/MACD.
            score += max(-20.0, min(20.0, change_pct * 4.0))
            evidence.append({"metric": "daily_change_pct", "value": change_pct})

        if current is not None and high is not None and low is not None and high >= low:
            span = high - low
            if span > 0:
                position = (current - low) / span
                score += (position - 0.5) * 20.0
                evidence.append({"metric": "intraday_position", "value": position})

        result = {
            "score": round(max(0.0, min(100.0, score)), 2),
            "available": bool(evidence),
            "evidence": evidence,
            "history_required_for": ["RSI", "MACD", "EMA20", "SMA50", "SMA200", "ATR", "ADX", "Bollinger"],
            "data_quality": "snapshot_only",
        }
        context.technical_result = result
        return result


def _num(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if isfinite(number) else None
