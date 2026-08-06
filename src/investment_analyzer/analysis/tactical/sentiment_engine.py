"""Evidence-based tactical sentiment engine.

This module intentionally does not fabricate sentiment. It accepts normalized
news/event records and returns N/D when no usable evidence is supplied.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from .tactical_models import Evidence, TacticalSignal


class SentimentEngine:
    POSITIVE = {"positive", "bullish", "upgrade", "beat", "strong", "growth", "buy"}
    NEGATIVE = {"negative", "bearish", "downgrade", "miss", "weak", "decline", "sell"}

    def analyze(self, news: Iterable[Mapping[str, Any]] | None) -> TacticalSignal:
        records = list(news or [])
        usable = []
        evidence = []
        for record in records:
            text = " ".join(str(record.get(k, "")) for k in ("title", "summary", "headline", "sentiment" )).lower()
            if not text.strip():
                continue
            pos = sum(1 for token in self.POSITIVE if token in text)
            neg = sum(1 for token in self.NEGATIVE if token in text)
            if pos == 0 and neg == 0:
                continue
            signal = 1 if pos > neg else -1 if neg > pos else 0
            usable.append(signal)
            evidence.append(Evidence(
                source=str(record.get("source", "unknown")),
                kind="news_sentiment",
                value=signal,
                timestamp=str(record.get("published_at", "")) or None,
                note=str(record.get("title", record.get("headline", ""))),
            ))

        if not usable:
            return TacticalSignal(
                score=None,
                available=False,
                confidence=0.0,
                evidence=evidence,
                warnings=["Sentiment no disponible: no hay noticias/eventos con señal interpretable"],
            )

        balance = sum(usable) / len(usable)
        score = round(50.0 + 50.0 * balance, 2)
        confidence = round(min(100.0, 50.0 + len(usable) * 5.0), 2)
        return TacticalSignal(score=score, available=True, confidence=confidence, evidence=evidence)
