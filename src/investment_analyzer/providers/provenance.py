"""V12 provider provenance and cross-source validation.

This module is deliberately provider-agnostic. It does not fetch data and
never chooses a source silently when two sources disagree materially.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import date, datetime
from typing import Any, Iterable


@dataclass(frozen=True, slots=True)
class DataPoint:
    field: str
    value: float | int | str | None
    provider: str
    period: str | None = None
    as_of: str | None = None
    quality: str = "MEDIUM"
    role: str = "VOTE"
    source_symbol: str | None = None
    unit: str | None = None

    def as_dict(self):
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ValidationResult:
    field: str
    status: str
    consensus_value: Any
    sources: tuple[str, ...]
    spread_pct: float | None
    confidence: float
    message: str

    def as_dict(self):
        return asdict(self)


class ProvenanceValidator:
    """Validate normalized financial values from multiple providers."""

    DEFAULT_TOLERANCES = {
        "ffo": 0.05,
        "affo": 0.05,
        "ebitda": 0.05,
        "net_debt": 0.05,
        "interest_expense": 0.08,
        "property_value": 0.10,
        "shares_outstanding": 0.01,
        "distribution": 0.05,
    }

    QUALITY_SCORE = {
        "HIGH": 100.0,
        "MEDIUM_HIGH": 90.0,
        "MEDIUM": 75.0,
        "LOW_MEDIUM": 60.0,
        "LOW": 40.0,
    }

    def __init__(self, tolerances: dict[str, float] | None = None):
        self.tolerances = {**self.DEFAULT_TOLERANCES, **(tolerances or {})}

    @staticmethod
    def _numeric(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def validate(self, points: Iterable[DataPoint], field: str) -> ValidationResult:
        selected = [p for p in points if p.field == field and self._numeric(p.value) is not None]
        if not selected:
            return ValidationResult(field, "MISSING", None, (), None, 0.0, "No hay valor numérico verificable")

        values = [self._numeric(p.value) for p in selected]
        providers = tuple(dict.fromkeys(p.provider for p in selected))
        if len(values) == 1:
            q = self.QUALITY_SCORE.get(selected[0].quality.upper(), 50.0)
            return ValidationResult(field, "SINGLE_SOURCE", values[0], providers, None, q, "Valor disponible en una sola fuente")

        reference = sum(values) / len(values)
        spread = (max(values) - min(values)) / abs(reference) if reference else 0.0
        tolerance = self.tolerances.get(field, 0.05)
        if spread <= tolerance:
            confidence = min(100.0, 75.0 + (len(providers) - 2) * 5.0 + (tolerance - spread) * 100.0)
            return ValidationResult(field, "CONSISTENT", reference, providers, spread * 100.0, round(confidence, 2), "Fuentes dentro de tolerancia")

        return ValidationResult(field, "CONFLICT", None, providers, spread * 100.0, max(20.0, 55.0 - spread * 100.0), "Conflicto material entre proveedores; no se selecciona una fuente arbitrariamente")

    def validate_many(self, points: Iterable[DataPoint], fields: Iterable[str]) -> dict[str, ValidationResult]:
        points = tuple(points)
        return {field: self.validate(points, field) for field in fields}

    @staticmethod
    def overall_confidence(results: dict[str, ValidationResult]) -> float:
        if not results:
            return 0.0
        return round(sum(r.confidence for r in results.values()) / len(results), 2)
