"""Evidence-based Smart Money proxy signals for V11.

This is deliberately a proxy engine. It does not claim access to dark-pool,
options-flow, or institutional order-book data unless those records are
explicitly supplied by a provider.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from investment_analyzer.common.models import PriceHistory
from .tactical_models import Evidence, TacticalSignal


class SmartMoneyEngine:
    """Estimate price/volume accumulation pressure from observable data."""

    @staticmethod
    def _rows(history: PriceHistory | Iterable[Mapping[str, Any]] | None):
        if history is None:
            return []
        if isinstance(history, PriceHistory):
            size = min(len(history.close), len(history.volume))
            return [
                {
                    "close": history.close[i],
                    "volume": history.volume[i],
                    "date": history.dates[i] if i < len(history.dates) else None,
                }
                for i in range(size)
            ]
        return list(history)

    def analyze(self, history: PriceHistory | Iterable[Mapping[str, Any]] | None) -> TacticalSignal:
        rows = self._rows(history)
        if len(rows) < 2:
            return TacticalSignal(
                score=None,
                available=False,
                confidence=0.0,
                warnings=["Smart Money no disponible: histórico insuficiente"],
            )

        observations: list[int] = []
        evidence: list[Evidence] = []
        for previous, current in zip(rows[:-1], rows[1:]):
            try:
                prev_close = float(previous.get("close"))
                close = float(current.get("close"))
                volume = float(current.get("volume"))
                prev_volume = float(previous.get("volume"))
            except (TypeError, ValueError):
                continue
            if prev_close <= 0 or prev_volume <= 0:
                continue

            price_change = (close / prev_close) - 1.0
            volume_ratio = volume / prev_volume
            if volume_ratio < 1.2:
                continue

            signal = 1 if price_change > 0 else -1 if price_change < 0 else 0
            observations.append(signal)
            evidence.append(Evidence(
                source="price_volume_history",
                kind="relative_volume_pressure",
                value={"price_change": round(price_change, 6), "volume_ratio": round(volume_ratio, 3), "signal": signal},
                timestamp=str(current.get("date", current.get("timestamp", ""))) or None,
                note="Proxy price/volume; no institutional flow claim",
            ))

        if not observations:
            return TacticalSignal(
                score=None,
                available=False,
                confidence=0.0,
                evidence=evidence,
                warnings=["Smart Money no disponible: no hubo observaciones de volumen relativo interpretable"],
            )

        balance = sum(observations) / len(observations)
        score = round(50.0 + 50.0 * balance, 2)
        confidence = round(min(100.0, 40.0 + len(observations) * 3.0), 2)
        return TacticalSignal(
            score=score,
            available=True,
            confidence=confidence,
            evidence=evidence,
            warnings=["Señal Smart Money es un proxy precio/volumen; no representa dark pool ni opciones institucionales"],
        )
