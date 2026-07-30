"""
decision_engine.py
Investment Analyzer v11

Motor de decisión transparente basado en puntuaciones ponderadas.

Compatible con la v10.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


# ----------------------------------------------------------------------
# CONFIGURACIÓN
# ----------------------------------------------------------------------

STRATEGIC_WEIGHTS = {
    "fundamental": 0.35,
    "valuation": 0.30,
    "comparables": 0.10,
    "macro": 0.05,
    "risk": 0.20,
}

TACTICAL_WEIGHTS = {
    "technical": 0.45,
    "sentiment": 0.20,
    "smart_money": 0.20,
    "macro": 0.15,
}


# ----------------------------------------------------------------------
# MODELOS
# ----------------------------------------------------------------------

@dataclass
class ScoreComponent:

    name: str
    score: float
    weight: float
    explanation: str = ""

    @property
    def weighted(self) -> float:
        return self.score * self.weight


@dataclass
class DecisionResult:

    strategic_score: float

    tactical_score: float

    strategic_decision: str

    tactical_decision: str

    confidence: float

    strategic_breakdown: List[ScoreComponent] = field(default_factory=list)

    tactical_breakdown: List[ScoreComponent] = field(default_factory=list)

    red_flags: List[str] = field(default_factory=list)

    strengths: List[str] = field(default_factory=list)


# ----------------------------------------------------------------------
# ENGINE
# ----------------------------------------------------------------------

class DecisionEngine:

    BUY = 80

    ACCUMULATE = 70

    HOLD = 55

    REDUCE = 40

    @staticmethod
    def _decision(score: float) -> str:

        if score >= DecisionEngine.BUY:
            return "COMPRAR"

        if score >= DecisionEngine.ACCUMULATE:
            return "ACUMULAR"

        if score >= DecisionEngine.HOLD:
            return "MANTENER"

        if score >= DecisionEngine.REDUCE:
            return "REDUCIR"

        return "VENDER"

    # --------------------------------------------------------------

    def strategic(self, data: Dict[str, float]):

        items = []

        total = 0.0

        for key, weight in STRATEGIC_WEIGHTS.items():

            value = float(data.get(key, 50))

            component = ScoreComponent(
                name=key,
                score=value,
                weight=weight,
            )

            items.append(component)

            total += component.weighted

        return total, items

    # --------------------------------------------------------------

    def tactical(self, data: Dict[str, float]):

        items = []

        total = 0.0

        for key, weight in TACTICAL_WEIGHTS.items():

            value = float(data.get(key, 50))

            component = ScoreComponent(
                name=key,
                score=value,
                weight=weight,
            )

            items.append(component)

            total += component.weighted

        return total, items

    # --------------------------------------------------------------

    @staticmethod
    def confidence(
        provider_quality: float,
        freshness: float,
        consistency: float,
        completeness: float,
    ):

        return round(

            provider_quality * 0.30
            + freshness * 0.20
            + consistency * 0.30
            + completeness * 0.20,

            2,

        )

    # --------------------------------------------------------------

    def evaluate(

        self,

        strategic_scores: Dict[str, float],

        tactical_scores: Dict[str, float],

        confidence_inputs: Dict[str, float],

        strengths=None,

        red_flags=None,

    ) -> DecisionResult:

        strategic_total, strategic_items = self.strategic(strategic_scores)

        tactical_total, tactical_items = self.tactical(tactical_scores)

        confidence = self.confidence(

            provider_quality=confidence_inputs.get(
                "provider_quality",
                80,
            ),

            freshness=confidence_inputs.get(
                "freshness",
                80,
            ),

            consistency=confidence_inputs.get(
                "consistency",
                80,
            ),

            completeness=confidence_inputs.get(
                "completeness",
                80,
            ),

        )

        return DecisionResult(

            strategic_score=round(strategic_total, 2),

            tactical_score=round(tactical_total, 2),

            strategic_decision=self._decision(strategic_total),

            tactical_decision=self._decision(tactical_total),

            confidence=confidence,

            strategic_breakdown=strategic_items,

            tactical_breakdown=tactical_items,

            strengths=strengths or [],

            red_flags=red_flags or [],

        )

    # --------------------------------------------------------------

    @staticmethod
    def print_summary(result: DecisionResult):

        print("=" * 80)

        print("DECISION ENGINE")

        print("=" * 80)

        print()

        print(f"Estrategico : {result.strategic_decision}")

        print(f"Puntuacion  : {result.strategic_score:.2f}")

        print()

        print(f"Tactico     : {result.tactical_decision}")

        print(f"Puntuacion  : {result.tactical_score:.2f}")

        print()

        print(f"Confianza   : {result.confidence:.1f}%")

        print()

        print("DESGLOSE ESTRATEGICO")

        print("-" * 80)

        for item in result.strategic_breakdown:

            print(
                f"{item.name:15s}"
                f"{item.score:8.2f}"
                f"{item.weighted:10.2f}"
            )

        print()

        print("DESGLOSE TACTICO")

        print("-" * 80)

        for item in result.tactical_breakdown:

            print(
                f"{item.name:15s}"
                f"{item.score:8.2f}"
                f"{item.weighted:10.2f}"
            )

        print()

        if result.strengths:

            print("FORTALEZAS")

            for s in result.strengths:

                print(" +", s)

            print()

        if result.red_flags:

            print("RED FLAGS")

            for s in result.red_flags:

                print(" -", s)

            print()