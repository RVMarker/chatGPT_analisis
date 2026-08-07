"""Transparent V11 decision engine."""
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
    def breakdown_dict(self):
        return {"strategic": [x.as_dict() for x in self.strategic_breakdown], "tactical": [x.as_dict() for x in self.tactical_breakdown]}

class DecisionEngine:
    BUY, ACCUMULATE, HOLD, REDUCE = 80.0, 70.0, 50.0, 35.0
    def __init__(self): validate_weights()
    @classmethod
    def _decision(cls, score):
        if score is None: return "N/D"
        if score >= cls.BUY: return "COMPRAR"
        if score >= cls.ACCUMULATE: return "ACUMULAR"
        if score >= cls.HOLD: return "MANTENER"
        if score >= cls.REDUCE: return "REDUCIR"
        return "VENDER"
    @staticmethod
    def _score(value, default=None):
        if value is None: return default
        try: return max(0.0, min(100.0, float(value)))
        except (TypeError, ValueError): return default
    def _weighted(self, data: Mapping[str, object], weights: Mapping[str, float]):
        items = []
        for key, weight in weights.items():
            raw = data.get(key)
            available = raw is not None and not (isinstance(raw, Mapping) and raw.get("available") is False)
            value = raw.get("score") if isinstance(raw, Mapping) else raw
            score = self._score(value) if available else None
            items.append(ScoreComponent(key, score, weight, "Disponible" if score is not None else "NO DISPONIBLE — no participa en el promedio", score is not None))
        available_items = [x for x in items if x.available]
        if not available_items: return None, items, ["Ningún componente disponible; veredicto N/D"]
        total_weight = sum(x.weight for x in available_items)
        for x in available_items: x.weight /= total_weight
        return sum(x.weighted for x in available_items), items, []
    def strategic(self, data): return self._weighted(data, STRATEGIC)
    def tactical(self, data): return self._weighted(data, TACTICAL)
    @staticmethod
    def confidence(provider_quality, freshness, consistency, completeness, technical_data_quality=100.0):
        values = [max(0.0, min(100.0, float(v))) for v in [provider_quality, freshness, consistency, completeness, technical_data_quality]]
        return round(values[0]*.27 + values[1]*.18 + values[2]*.27 + values[3]*.18 + values[4]*.10, 2)
    def evaluate(self, strategic_scores, tactical_scores, confidence_inputs, strengths=None, red_flags=None, contextual=None):
        ss, si, sw = self.strategic(strategic_scores); ts, ti, tw = self.tactical(tactical_scores)
        confidence = self.confidence(confidence_inputs.get("provider_quality",80), confidence_inputs.get("freshness",80), confidence_inputs.get("consistency",80), confidence_inputs.get("completeness",80), confidence_inputs.get("technical_data_quality",100))
        context = {k:s for k,v in (contextual or {}).items() if (s:=self._score(v)) is not None}
        flags = list(red_flags or []) + sw + tw
        flags += [f"{x.name}: NO DISPONIBLE; excluido del promedio ponderado" for x in si+ti if not x.available]
        return DecisionResult(round(ss,2) if ss is not None else None, round(ts,2) if ts is not None else None, self._decision(ss), self._decision(ts), confidence, si, ti, list(dict.fromkeys(flags)), list(strengths or []), context)
    @staticmethod
    def print_summary(result):
        print("="*80); print("DECISION ENGINE V11"); print("="*80)
        print(f"Estratégico (años): {result.strategic_decision} | {result.strategic_score if result.strategic_score is not None else 'N/D'}/100")
        print(f"Táctico (semanas):  {result.tactical_decision} | {result.tactical_score if result.tactical_score is not None else 'N/D'}/100")
        print(f"Confianza:          {result.confidence:.1f}%")
