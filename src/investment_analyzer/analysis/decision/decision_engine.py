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

    def as_dict(self):
        return {"name": self.name, "score": round(self.score, 2) if self.score is not None else None,
                "weight": round(self.weight, 4), "weighted_contribution": round(self.weighted, 2),
                "contribution_pct": round(self.contribution_pct, 2), "explanation": self.explanation,
                "available": self.available}


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
    strategic_coverage: float = 100.0
    tactical_coverage: float = 100.0
    strategic_sufficient: bool = True
    tactical_sufficient: bool = True

    def breakdown_dict(self):
        return {"strategic": [item.as_dict() for item in self.strategic_breakdown],
                "tactical": [item.as_dict() for item in self.tactical_breakdown]}


class DecisionEngine:
    BUY, ACCUMULATE, HOLD, REDUCE = 80.0, 70.0, 50.0, 35.0
    MIN_DECISION_COVERAGE = 50.0

    def __init__(self) -> None:
        validate_weights()

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

    @staticmethod
    def _normalize_weight(weight, total):
        return float(Decimal(str(weight)) / Decimal(str(total)))

    def _weighted(self, data: Mapping[str, object], weights: Mapping[str, float]):
        items = []
        for key, weight in weights.items():
            raw = data.get(key)
            available = raw is not None and not (isinstance(raw, Mapping) and raw.get("available") is False)
            score = self._score(raw.get("score")) if isinstance(raw, Mapping) and available else self._score(raw) if available else None
            items.append(ScoreComponent(key, score, weight, available=available and score is not None,
                                        explanation="Disponible" if available and score is not None else "NO DISPONIBLE — no participa en el promedio"))
        available_items = [item for item in items if item.available]
        if not available_items: return None, items, ["Ningún componente disponible; veredicto N/D"]
        total_weight = sum(item.weight for item in available_items)
        for item in available_items: item.weight = self._normalize_weight(item.weight, total_weight)
        return sum(item.weighted for item in available_items), items, []

    @staticmethod
    def _coverage(items):
        return round(100.0 * sum(item.available for item in items) / len(items), 2) if items else 0.0

    def strategic(self, data): return self._weighted(data, STRATEGIC)
    def tactical(self, data): return self._weighted(data, TACTICAL)

    @staticmethod
    def _quality_score(value):
        if value is None: return 100.0
        if isinstance(value, (int, float)): return max(0.0, min(100.0, float(value)))
        return {"HIGH": 100.0, "MEDIUM": 75.0, "LOW": 50.0}.get(str(value).upper(), 100.0)

    @staticmethod
    def confidence(provider_quality, freshness, consistency, completeness, technical_data_quality=100.0,
                   coverage=100.0, valuation_quality=None):
        values = [max(0.0, min(100.0, float(v))) for v in [provider_quality, freshness, consistency, completeness, technical_data_quality]]
        q = DecisionEngine._quality_score(valuation_quality)
        base = values[0]*0.243 + values[1]*0.162 + values[2]*0.243 + values[3]*0.162 + values[4]*0.090 + q*0.100
        return round(base * max(0.0, min(100.0, float(coverage))) / 100.0, 2)

    def evaluate(self, strategic_scores, tactical_scores, confidence_inputs, strengths=None, red_flags=None, contextual=None):
        strategic_total, strategic_items, strategic_warnings = self.strategic(strategic_scores)
        tactical_total, tactical_items, tactical_warnings = self.tactical(tactical_scores)
        strategic_coverage, tactical_coverage = self._coverage(strategic_items), self._coverage(tactical_items)
        coverage = round((strategic_coverage + tactical_coverage) / 2.0, 2)
        valuation_quality = confidence_inputs.get("valuation_quality")
        args = (confidence_inputs.get("provider_quality",80), confidence_inputs.get("freshness",80), confidence_inputs.get("consistency",80), confidence_inputs.get("completeness",80), confidence_inputs.get("technical_data_quality",100))
        base_confidence = self.confidence(*args, 100, valuation_quality)
        confidence = self.confidence(*args, coverage, valuation_quality)
        context = {}
        for key, value in (contextual or {}).items():
            score = self._score(value)
            if score is not None: context[key] = score
        strategic_sufficient = strategic_total is not None and strategic_coverage >= self.MIN_DECISION_COVERAGE
        tactical_sufficient = tactical_total is not None and tactical_coverage >= self.MIN_DECISION_COVERAGE
        flags = list(red_flags or []) + strategic_warnings + tactical_warnings
        for item in strategic_items + tactical_items:
            if not item.available: flags.append(f"{item.name}: NO DISPONIBLE; excluido del promedio ponderado")
        if valuation_quality is not None and str(valuation_quality).upper() != "HIGH":
            flags.append(f"Calidad de valoración {str(valuation_quality).upper()}: reduce confianza, pero no altera el score ni el veredicto")
        if not strategic_sufficient and strategic_total is not None: flags.append(f"Cobertura estratégica insuficiente: {strategic_coverage:.1f}%; el veredicto estratégico es una señal, no una conclusión robusta")
        if not tactical_sufficient and tactical_total is not None: flags.append(f"Cobertura táctica insuficiente: {tactical_coverage:.1f}%; el veredicto táctico es una señal, no una conclusión robusta")
        if coverage < 100: flags.append(f"Cobertura de señales decisorias: {coverage:.1f}%")
        return DecisionResult(round(strategic_total,2) if strategic_total is not None else None,
                              round(tactical_total,2) if tactical_total is not None else None,
                              self._decision(strategic_total), self._decision(tactical_total), confidence,
                              strategic_items, tactical_items, list(dict.fromkeys(flags)), list(strengths or []), context,
                              coverage, base_confidence, strategic_coverage, tactical_coverage,
                              strategic_sufficient, tactical_sufficient)

    @staticmethod
    def print_summary(result):
        strategic = f"{result.strategic_score:.2f}/100" if result.strategic_score is not None else "N/D"
        tactical = f"{result.tactical_score:.2f}/100" if result.tactical_score is not None else "N/D"
        print("=" * 80); print("DECISION ENGINE V11"); print("=" * 80)
        print(f"Estratégico (años): {result.strategic_decision} | {strategic}")
        print(f"Táctico (semanas):  {result.tactical_decision} | {tactical}")
        print(f"Confianza:          {result.confidence:.1f}%")
        print(f"Cobertura señales:  {result.data_coverage:.1f}%")
