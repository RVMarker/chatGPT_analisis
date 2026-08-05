"""Transparent V11 decision engine.

Strategic horizon: years. Tactical horizon: weeks.
Comparables and macro are contextual evidence only and never vote in either
verdict. This prevents double-counting valuation context and makes the score
explainable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .decision_weights import STRATEGIC, TACTICAL, validate_weights


@dataclass(slots=True)
class ScoreComponent:
    name: str
    score: float
    weight: float
    explanation: str = ""

    @property
    def weighted(self) -> float:
        return self.score * self.weight


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


class DecisionEngine:
    """Convert normalized 0-100 evidence into transparent verdicts."""

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
    def _score(value: object, default: float = 50.0) -> float:
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = default
        return max(0.0, min(100.0, value))

    def _weighted(self, data: Mapping[str, object], weights: Mapping[str, float]):
        items: list[ScoreComponent] = []
        for key, weight in weights.items():
            score = self._score(data.get(key, 50.0))
            items.append(ScoreComponent(key, score, weight))
        return sum(item.weighted for item in items), items

    def strategic(self, data: Mapping[str, object]):
        return self._weighted(data, STRATEGIC)

    def tactical(self, data: Mapping[str, object]):
        return self._weighted(data, TACTICAL)

    @staticmethod
    def confidence(
        provider_quality: float,
        freshness: float,
        consistency: float,
        completeness: float,
    ) -> float:
        values = [provider_quality, freshness, consistency, completeness]
        values = [max(0.0, min(100.0, float(v))) for v in values]
        return round(
            values[0] * 0.30
            + values[1] * 0.20
            + values[2] * 0.30
            + values[3] * 0.20,
            2,
        )

    def evaluate(
        self,
        strategic_scores: Mapping[str, object],
        tactical_scores: Mapping[str, object],
        confidence_inputs: Mapping[str, object],
        strengths: list[str] | None = None,
        red_flags: list[str] | None = None,
        contextual: Mapping[str, object] | None = None,
    ) -> DecisionResult:
        strategic_total, strategic_items = self.strategic(strategic_scores)
        tactical_total, tactical_items = self.tactical(tactical_scores)
        confidence = self.confidence(
            confidence_inputs.get("provider_quality", 80),
            confidence_inputs.get("freshness", 80),
            confidence_inputs.get("consistency", 80),
            confidence_inputs.get("completeness", 80),
        )
        context = {
            key: self._score(value)
            for key, value in (contextual or {}).items()
        }
        return DecisionResult(
            strategic_score=round(strategic_total, 2),
            tactical_score=round(tactical_total, 2),
            strategic_decision=self._decision(strategic_total),
            tactical_decision=self._decision(tactical_total),
            confidence=confidence,
            strategic_breakdown=strategic_items,
            tactical_breakdown=tactical_items,
            strengths=list(strengths or []),
            red_flags=list(red_flags or []),
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
            print(f"  {item.name:15s} score={item.score:6.2f} peso={item.weight:.0%} aporte={item.weighted:6.2f}")
        print("\nDESGLOSE TÁCTICO")
        for item in result.tactical_breakdown:
            print(f"  {item.name:15s} score={item.score:6.2f} peso={item.weight:.0%} aporte={item.weighted:6.2f}")
        if result.contextual:
            print("\nCONTEXTO (NO VOTA)")
            for key, value in result.contextual.items():
                print(f"  {key:15s} {value:6.2f}")
        if result.strengths:
            print("\nFORTALEZAS")
            for item in result.strengths:
                print(f"  + {item}")
        if result.red_flags:
            print("\nRED FLAGS")
            for item in result.red_flags:
                print(f"  - {item}")
