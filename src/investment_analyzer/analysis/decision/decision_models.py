"""
decision_models.py

Modelos utilizados por el Decision Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class DecisionFactor:

    name: str

    score: float

    weight: float

    source: str

    explanation: str = ""

    category: str = ""

    @property
    def contribution(self) -> float:
        return self.score * self.weight


@dataclass(slots=True)
class DecisionBreakdown:

    factors: list[DecisionFactor] = field(default_factory=list)

    @property
    def total(self):

        return sum(f.contribution for f in self.factors)

    def add(

        self,

        name,

        score,

        weight,

        source,

        explanation="",

        category="",

    ):

        self.factors.append(

            DecisionFactor(

                name=name,

                score=score,

                weight=weight,

                source=source,

                explanation=explanation,

                category=category,

            )

        )


@dataclass(slots=True)
class DecisionSummary:

    score: float

    verdict: str

    breakdown: DecisionBreakdown