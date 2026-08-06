"""Pure-Python technical indicators from OHLCV history.

No network access is performed here. The engine returns only indicators for
which enough observations exist and explicitly reports missing requirements.
"""
from __future__ import annotations

from math import sqrt


def _clean(values):
    return [float(v) for v in values if v is not None]


def sma(values, period):
    x = _clean(values)
    return sum(x[-period:]) / period if len(x) >= period else None


def ema(values, period):
    x = _clean(values)
    if len(x) < period:
        return None
    value = sum(x[:period]) / period
    alpha = 2 / (period + 1)
    for item in x[period:]:
        value = alpha * item + (1 - alpha) * value
    return value


def stddev(values, period):
    x = _clean(values)
    if len(x) < period:
        return None
    window = x[-period:]
    mean = sum(window) / period
    return sqrt(sum((v - mean) ** 2 for v in window) / period)


def bollinger(values, period=20, deviations=2):
    middle = sma(values, period)
    sd = stddev(values, period)
    if middle is None or sd is None:
        return None
    return {"middle": middle, "upper": middle + deviations * sd, "lower": middle - deviations * sd}


def rsi(values, period=14):
    x = _clean(values)
    if len(x) < period + 1:
        return None
    changes = [x[i] - x[i - 1] for i in range(1, len(x))]
    gains = [max(c, 0) for c in changes]
    losses = [max(-c, 0) for c in changes]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(changes)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0:
        return 100.0
    return 100 - (100 / (1 + avg_gain / avg_loss))


def macd(values, fast=12, slow=26, signal=9):
    x = _clean(values)
    if len(x) < slow + signal - 1:
        return None
    # Build the MACD series so the signal line is based on historical MACD values.
    macd_series = []
    for end in range(slow, len(x) + 1):
        fast_value = ema(x[:end], fast)
        slow_value = ema(x[:end], slow)
        macd_series.append(fast_value - slow_value)
    if len(macd_series) < signal:
        return None
    line = macd_series[-1]
    signal_line = ema(macd_series, signal)
    return {"macd": line, "signal": signal_line, "histogram": line - signal_line}


def atr(high, low, close, period=14):
    h, l, c = map(_clean, (high, low, close))
    n = min(len(h), len(l), len(c))
    if n < period + 1:
        return None
    tr = []
    for i in range(1, n):
        tr.append(max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])))
    return sum(tr[-period:]) / period if len(tr) >= period else None


def calculate_indicators(history):
    close = history.close
    result = {
        "ema20": ema(close, 20),
        "sma20": sma(close, 20),
        "sma50": sma(close, 50),
        "sma200": sma(close, 200),
        "rsi14": rsi(close, 14),
        "macd": macd(close),
        "bollinger20": bollinger(close, 20),
        "atr14": atr(history.high, history.low, close, 14),
    }
    result["requirements"] = {
        "ema20": len(close) >= 20,
        "sma50": len(close) >= 50,
        "sma200": len(close) >= 200,
        "rsi14": len(close) >= 15,
        "macd": len(close) >= 34,
        "bollinger20": len(close) >= 20,
        "atr14": min(len(history.high), len(history.low), len(close)) >= 15,
    }
    return result
