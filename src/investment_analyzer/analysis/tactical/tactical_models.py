"""Normalized models for tactical evidence used by V11."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Evidence:
    source: str
    kind: str
    value: Any = None
    timestamp: str | None = None
    available: bool = True
    note: str = ""


@dataclass(slots=True)
class TacticalSignal:
    score: float | None
    available: bool
    confidence: float
    evidence: list[Evidence] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "available": self.available,
            "confidence": self.confidence,
            "evidence": [asdict(e) for e in self.evidence],
            "warnings": list(self.warnings),
        }
