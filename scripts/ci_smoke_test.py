"""Lightweight CI smoke test that does not require external market APIs."""
from __future__ import annotations

from investment_analyzer.analysis.decision.decision_engine import DecisionEngine
from investment_analyzer.analysis.tactical.sentiment_engine import SentimentEngine
from investment_analyzer.analysis.tactical.smart_money_engine import SmartMoneyEngine


def main() -> int:
    sentiment = SentimentEngine().analyze([])
    smart_money = SmartMoneyEngine().analyze([])
    engine = DecisionEngine()
    score, breakdown, _ = engine.tactical({
        "technical": 80,
        "sentiment": sentiment.score,
        "smart_money": smart_money.score,
    })
    assert score == 80.0
    assert sentiment.score is None
    assert smart_money.score is None
    assert any(item.name == "technical" and item.available for item in breakdown)
    print("CI smoke test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
