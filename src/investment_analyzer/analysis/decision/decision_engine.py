"""Transparent V11 decision engine.

Strategic horizon: years. Tactical horizon: weeks.
Comparables and macro are contextual evidence only and never vote in either
verdict. Unavailable evidence is not silently converted to a neutral 50.
"""
from __future__ import annotations

from dataclasses import dataclass, field
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
        return {
            "name": self.name,
            "score": round(self.score, 2) if self.score is not None else None,
            "weight": round(self.weight, 4),
            "weighted_contribution": round(self.weighted, 2),
            "contribution_pct": round(self.contribution_pct, 2),
            "explanation": self.explanation,
            "available": self.available,
        }


@dataclass(slots=True)
class DecisionResult:
    strategic_score: float
    tactical_score: float
    strategic_decision: str
    tactical_decision: str
    confidence: float
    strategic_breakdown: list[ScoreComponent] = field(default_factory=list)
    tactical_breakdown: list[ScoreComponent] = field(default_factory=list)
    red_flags: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    contextual: dict[str, float] = field(default_factory=dict)

    def breakdown_dict(self) -> dict[str, list[dict[str, object]]]:
        return {
            "strategic": [item.as_dict() for item in self.strategic_breakdown],
            "tactical": [item.as_dict() for item in self.tactical_breakdown],
        }


class DecisionEngine:
    BUY = 80.0
    ACCUMULATE = 70.0
    HOLD = 50.0
    REDUCE = 35.0

    def __init__(self) -> None:
        validate_weights()

    @classmethod
    def _decision(cls, score: float) -> str:
        if score >= cls.BUY:
            return "COMPRAR"
        if score >= cls.ACCUMULATE:
            return "ACUMULAR"
        if score >= cls.HOLD:
            return "MANTENER"
        if score >= cls.REDUCE:
            return "REDUCIR"
        return "VENDER"

    @staticmethod
    def _score(value: object, default: float | None = 50.0) -> float | None:
        if value is None:
            return default
        try:
            return max(0.0, min(100.0, float(value)))
        except (TypeError, ValueError):
            return default

    def _weighted(self, data: Mapping[str, object], weights: Mapping[str, float]):
        available_items: list[ScoreComponent] = []
        unavailable: list[ScoreComponent] = []
        for key, weight in weights.items():
            raw = data.get(key)
            available = raw is not None and not (
                isinstance(raw, Mapping) and raw.get("available") is False
            )
            score = self._score(
                raw.get("score") if isinstance(raw, Mapping) else raw,
                default=None,
            ) if available else None
            item = ScoreComponent(
                key,
                score,
                weight,
                available=available,
                explanation="Disponible" if available else "NO DISPONIBLE — no participa en el promedio",
            )
            (available_items if available else unavailable).append(item)

        if not available_items:
            return 50.0, unavailable, ["Ningún componente disponible"]

        effective_weight_total = sum(item.weight for item in available_items)
        for item in available_items:
            item.weight = item.weight / effective_weight_total
        total = sum(item.weighted for item in available_items)
        return total, available_items + unavailable, []

    def strategic(self, data: Mapping[str, object]):
        return self._weighted(data, STRATEGIC)

    def tactical(self, data: Mapping[str, object]):
        return self._weighted(data, TACTICAL)

    @staticmethod
    def confidence(provider_quality: float, freshness: float, consistency: float, completeness: float, technical_data_quality: float = 100.0) -> float:
        values = [provider_quality, freshness, consistency, completeness, technical_data_quality]
        values = [max(0.0, min(100.0, float(v))) for v in values]
        return round(values[0] * 0.27 + values[1] * 0.18 + values[2] * 0.27 + values[3] * 0.18 + values[4] * 0.10, 2)

    def evaluate(self, strategic_scores: Mapping[str, object], tactical_scores: Mapping[str, object], confidence_inputs: Mapping[str, object], strengths: list[str] | None = None, red_flags: list[str] | None = None, contextual: Mapping[str, object] | None = None) -> DecisionResult:
        strategic_total, strategic_items, strategic_warnings = self.strategic(strategic_scores)
        tactical_total, tactical_items, tactical_warnings = self.tactical(tactical_scores)
        confidence = self.confidence(
            confidence_inputs.get("provider_quality", 80),
            confidence_inputs.get("freshness", 80),
            confidence_inputs.get("consistency", 80),
            confidence_inputs.get("completeness", 80),
            confidence_inputs.get("technical_data_quality", 100),
        )
        context = {key: self._score(value) for key, value in (contextual or {}).items() if self._score(value) is not None}
        flags = list(red_flags or [])
        flags.extend(strategic_warnings + tactical_warnings)
        for item in strategic_items + tactical_items:
            if not item.available:
                flags.append(f"{item.name}: NO DISPONIBLE; excluido del promedio ponderado")
        return DecisionResult(
            strategic_score=round(strategic_total, 2),
            tactical_score=round(tactical_total, 2),
            strategic_decision=self._decision(strategic_total),
            tactical_decision=self._decision(tactical_total),
            confidence=confidence,
            strategic_breakdown=strategic_items,
            tactical_breakdown=tactical_items,
            strengths=list(strengths or []),
            red_flags=list(dict.fromkeys(flags)),
            contextual=context,
        )

    @staticmethod
    def print_summary(result: DecisionResult) -> None:
        print("=" * 80)
        print("DECISION ENGINE V11")
        print("=" * 80)
        print(f"Estratégico (años): {result.strategic_decision} | {result.strategic_score:.2f}/100")
        print(f"Táctico (semanas):  {result.tactical_decision} | {result.tactical_score:.2f}/100")
        print(f"Confianza:          {result.confidence:.1f}%")
        print("\nDESGLOSE ESTRATÉGICO")
        for item in result.strategic_breakdown:
            score = f"{item.score:.2f}" if item.score is not None else "N/D"
            print(f"  {item.name:15s} score={score:>6} peso={item.weight:.1%} aporte={item.weighted:6.2f} {'[NO DISP]' if not item.available else ''}")
        print("\nDESGLOSE TÁCTICO")
        for item in result.tactical_breakdown:
            score = f"{item.score:.2f}" if item.score is not None else "N/D"
            print(f"  {item.name:15s} score={score:>6} peso={item.weight:.1%} aporte={item.weighted:6.2f} {'[NO DISP]' if not item.available else ''}")
