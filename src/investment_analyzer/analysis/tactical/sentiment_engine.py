"""Evidence-based tactical sentiment engine.

This module intentionally does not fabricate sentiment. It accepts normalized
news/event records and returns N/D when no usable evidence is supplied.

A directional score is not treated as certainty: small samples are shrunk
back toward neutral (50/100). This prevents one positive or negative article
from producing an artificial 100/100 or 0/100 tactical signal.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from .tactical_models import Evidence, TacticalSignal


class SentimentEngine:
    POSITIVE = {"positive", "bullish", "upgrade", "beat", "strong", "growth", "buy"}
    NEGATIVE = {"negative", "bearish", "downgrade", "miss", "weak", "decline", "sell"}

    @staticmethod
    def _evidence_confidence(sample_size: int) -> float:
        """Confidence from sample size, capped conservatively at 80%.

        One usable item is directional evidence, not a robust consensus.
        The score therefore remains useful while being explicitly shrunk
        toward neutral until the sample becomes larger.
        """
        if sample_size <= 0:
            return 0.0
        return round(min(80.0, 50.0 + 10.0 * min(sample_size, 3)), 2)

    def analyze(self, news: Iterable[Mapping[str, Any]] | None) -> TacticalSignal:
        records = list(news or [])
        usable = []
        evidence = []
        for record in records:
            text = " ".join(
                str(record.get(k, ""))
                for k in ("title", "summary", "headline", "sentiment")
            ).lower()
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
                metadata={"raw_score": None, "sample_size": 0, "evidence_confidence": 0.0},
            )

        balance = sum(usable) / len(usable)
        raw_score = round(50.0 + 50.0 * balance, 2)
        evidence_confidence = self._evidence_confidence(len(usable))
        # Shrink extreme directional readings toward neutral when evidence is scarce.
        score = round(50.0 + (raw_score - 50.0) * evidence_confidence / 100.0, 2)
        warnings = []
        if len(usable) < 3:
            warnings.append(
                f"Sentiment: muestra pequeña ({len(usable)} evidencia(s)); score ajustado hacia neutral"
            )

        return TacticalSignal(
            score=score,
            available=True,
            confidence=evidence_confidence,
            evidence=evidence,
            warnings=warnings,
            metadata={
                "raw_score": raw_score,
                "sample_size": len(usable),
                "evidence_confidence": evidence_confidence,
                "directional_balance": round(balance, 4),
            },
        )
