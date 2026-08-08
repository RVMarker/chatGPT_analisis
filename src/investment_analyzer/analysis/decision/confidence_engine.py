"""V12.5 confidence engine: coverage is based on usable evidence, not presence."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping

@dataclass(frozen=True, slots=True)
class ConfidenceResult:
    coverage: float
    data_quality: float
    confidence: float
    usable: int
    required: int
    blocked: tuple[str, ...]
    missing: tuple[str, ...]

class ConfidenceEngine:
    def evaluate(self, required_fields: list[str], validation: Mapping[str, Mapping] | None = None,
                 base_quality: float = 100.0) -> ConfidenceResult:
        validation = validation or {}
        required = len(required_fields)
        usable = 0
        blocked, missing = [], []
        qualities = []
        for field in required_fields:
            item = validation.get(field)
            if not item or item.get("status") == "MISSING":
                missing.append(field); continue
            q = float(item.get("confidence", 0.0)); qualities.append(q)
            if item.get("vote_allowed", False): usable += 1
            else: blocked.append(field)
        coverage = round(100.0 * usable / required, 2) if required else 0.0
        evidence_quality = sum(qualities) / len(qualities) if qualities else 0.0
        data_quality = round(min(float(base_quality), evidence_quality) if qualities else 0.0, 2)
        confidence = round((coverage * 0.60) + (data_quality * 0.40), 2)
        return ConfidenceResult(coverage, data_quality, confidence, usable, required, tuple(blocked), tuple(missing))
