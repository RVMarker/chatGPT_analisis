"""V12.1 provider confidence and source arbitration policy."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from .provenance import DataPoint, ProvenanceValidator, ValidationResult

@dataclass(frozen=True, slots=True)
class FieldDecision:
    field: str
    status: str
    value: float | int | str | None
    confidence: float
    vote_allowed: bool
    reason: str

class ProviderConfidence:
    """Turns provenance validation into an explicit data-usage policy."""
    BLOCK_ON_CONFLICT = {"ffo", "affo", "ebitda", "net_debt", "interest_expense", "property_value", "distribution"}
    MIN_SINGLE_SOURCE = 60.0

    def __init__(self, validator: ProvenanceValidator | None = None):
        self.validator = validator or ProvenanceValidator()

    def decide(self, points: Iterable[DataPoint], fields: Iterable[str]) -> dict[str, FieldDecision]:
        results = self.validator.validate_many(points, fields)
        out = {}
        for field, result in results.items():
            allowed = result.status != "MISSING"
            reason = result.message
            if result.status == "CONFLICT" and field in self.BLOCK_ON_CONFLICT:
                allowed = False
                reason = "CONFLICTO MATERIAL: bloqueado para decisión hasta resolver fuentes"
            elif result.status == "SINGLE_SOURCE" and result.confidence < self.MIN_SINGLE_SOURCE:
                allowed = False
                reason = "Fuente única con confianza insuficiente"
            out[field] = FieldDecision(field, result.status, result.consensus_value if allowed else None, result.confidence, allowed, reason)
        return out

    @staticmethod
    def score(decisions: dict[str, FieldDecision]) -> float:
        if not decisions:
            return 0.0
        return round(sum(x.confidence for x in decisions.values()) / len(decisions), 2)
