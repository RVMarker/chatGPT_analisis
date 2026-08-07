"""Transparent V11 decision engine.

Strategic horizon: years. Tactical horizon: weeks.
Comparables and macro are contextual evidence only and never vote in either
verdict. Unavailable evidence is not silently converted to a neutral 50.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Mapping

from .decision_weights import STRATEGIC, TACTICAL, validate_weights


@dataclass(slots=True)
class ScoreComponent:
    name: str
    score: float | None
    weight: float
    explanation: str = ""
    available: bool = True

    @property
    def weighted(self) -> float:
        return (self.score or 0.0) * self.weight

    @property
    def contribution_pct(self) -> float:
        return self.weighted

    def as_dict(self) -> dict[str, object]:
        return {"name": self.name, "score": round(self.score, 2) if self.score is not None else None, "weight": round(self.weight, 4), "weighted_contribution": round(self.weighted, 2), "contribution_pct": round(self.contribution_pct, 2), "explanation": self.explanation, "available": self.available}


@dataclass(slots=True)
class DecisionResult:
    strategic_score: float | None
    tactical_score: float | None
    strategic_decision: str
    tactical_decision: str
    confidence: float
    strategic_breakdown: list[ScoreComponent] = field(default_factory=list)
    tactical_breakdown: list[ScoreComponent] = field(default_factory=list)
    red_flags: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    contextual: dict[str, float] = field(default_factory=dict)
    data_coverage: float = 100.0
    base_confidence: float = 100.0

    def breakdown_dict(self) -> dict[str, list[dict[str, object]]]:
        return {"strategic": [item.as_dict() for item in self.strategic_breakdown], "tactical": [item.as_dict() for item in self.tactical_breakdown]}


class DecisionEngine:
    BUY = 80.0
    ACCUMULATE = 70.0
    HOLD = 50.0
    REDUCE = 35.0

    def __init__(self) -> None:
        validate_weights()

    @classmethod
    def _decision(cls, score: float | None) -> str:
        if score is None: return "N/D"
        if score >= cls.BUY: return "COMPRAR"
        if score >= cls.ACCUMULATE: return "ACUMULAR"
        if score >= cls.HOLD: return "MANTENER"
        if score >= cls.REDUCE: return "REDUCIR"
        return "VENDER"

    @staticmethod
    def _score(value: object, default: float | None = None) -> float | None:
        if value is None: return default
        try: return max(0.0, min(100.0, float(value)))
        except (TypeError, ValueError): return default

    @staticmethod
    def _normalize_weight(weight: float, total: float) -> float:
        return float(Decimal(str(weight)) / Decimal(str(total)))

    def _weighted(self, data: Mapping[str, object], weights: Mapping[str, float]):
        items = []
        for key, weight in weights.items():
            raw = data.get(key)
            available = raw is not None and not (isinstance(raw, Mapping) and raw.get("available") is False)
            score = self._score(raw.get("score")) if isinstance(raw, Mapping) and available else self._score(raw) if available else None
            items.append(ScoreComponent(key, score, weight, available=available and score is not None, explanation="Disponible" if available and score is not None else "NO DISPONIBLE — no participa en el promedio"))
        available_items = [item for item in items if item.available]
        if not available_items: return None, items, ["Ningún componente disponible; veredicto N/D"]
        total_weight = sum(item.weight for item in available_items)
        for item in available_items: item.weight = self._normalize_weight(item.weight, total_weight)
        return sum(item.weighted for item in available_items), items, []

    @staticmethod
    def _coverage(items: list[ScoreComponent]) -> float:
        return round(100.0 * sum(item.available for item in items) / len(items), 2) if items else 0.0

    def strategic(self, data): return self._weighted(data, STRATEGIC)
    def tactical(self, data): return self._weighted(data, TACTICAL)

    @staticmethod
    def confidence(provider_quality: float, freshness: float, consistency: float, completeness: float, technical_data_quality: float = 100.0, coverage: float = 100.0) -> float:
        values = [max(0.0, min(100.0, float(v))) for v in [provider_quality, freshness, consistency, completeness, technical_data_quality]]
        base = values[0] * .27 + values[1] * .18 + values[2] * .27 + values[3] * .18 + values[4] * .10
        return round(base * max(0.0, min(100.0, float(coverage))) / 100.0, 2)

    def evaluate(self, strategic_scores, tactical_scores, confidence_inputs, strengths=None, red_flags=None, contextual=None):
        strategic_total, strategic_items, strategic_warnings = self.strategic(strategic_scores)
        tactical_total, tactical_items, tactical_warnings = self.tactical(tactical_scores)
        coverage = round((self._coverage(strategic_items) + self._coverage(tactical_items)) / 2.0, 2)
        base_confidence = self.confidence(confidence_inputs.get("provider_quality", 80), confidence_inputs.get("freshness", 80), confidence_inputs.get("consistency", 80), confidence_inputs.get("completeness", 80), confidence_inputs.get("technical_data_quality", 100), 100)
        confidence = self.confidence(confidence_inputs.get("provider_quality", 80), confidence_inputs.get("freshness", 80), confidence_inputs.get("consistency", 80), confidence_inputs.get("completeness", 80), confidence_inputs.get("technical_data_quality", 100), coverage)
        context = {}
        for key, value in (contextual or {}).items():
            score = self._score(value)
            if score is not None: context[key] = score
        flags = list(red_flags or []) + strategic_warnings + tactical_warnings
        for item in strategic_items + tactical_items:
            if not item.available: flags.append(f"{item.name}: NO DISPONIBLE; excluido del promedio ponderado")
        if coverage < 100: flags.append(f"Cobertura de señales decisorias: {coverage:.1f}%")
        return DecisionResult(round(strategic_total, 2) if strategic_total is not None else None, round(tactical_total, 2) if tactical_total is not None else None, self._decision(strategic_total), self._decision(tactical_total), confidence, strategic_items, tactical_items, list(dict.fromkeys(flags)), list(strengths or []), context, coverage, base_confidence)

    @staticmethod
    def print_summary(result):
        print("=" * 80); print("DECISION ENGINE V11"); print("=" * 80)
        print(f"Estratégico (años): {result.strategic_decision} | {result.strategic_score:.2f}/100")
        print(f"Táctico (semanas):  {result.tactical_decision} | {result.tactical_score:.2f}/100")
        print(f"Confianza:          {result.confidence:.1f}%")
        print(f"Cobertura señales:  {result.data_coverage:.1f}%")
