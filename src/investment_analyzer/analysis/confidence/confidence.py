"""Nivel de confianza del análisis.

V11 semantics: ``missing`` is the percentage of expected data that is
missing (0 = nothing missing, 100 = everything missing). Missing data is a
penalty, never a positive contribution to confidence.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Confidence:
    value: float
    level: str


class ConfidenceEngine:
    @staticmethod
    def _bounded(value: float) -> float:
        return max(0.0, min(100.0, float(value)))

    @classmethod
    def evaluate(cls, providers, freshness, missing, agreement):
        providers = cls._bounded(providers)
        freshness = cls._bounded(freshness)
        missing = cls._bounded(missing)
        agreement = cls._bounded(agreement)

        completeness = 100.0 - missing
        score = (
            providers * 0.30
            + freshness * 0.25
            + agreement * 0.30
            + completeness * 0.15
        )
        score = round(score, 2)

        if score >= 90:
            level = "Muy Alta"
        elif score >= 80:
            level = "Alta"
        elif score >= 65:
            level = "Media"
        else:
            level = "Baja"

        return Confidence(score, level)
