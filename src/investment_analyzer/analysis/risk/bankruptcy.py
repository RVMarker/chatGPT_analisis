"""
Combina Altman + Piotroski + Beneish.
"""

from __future__ import annotations

from dataclasses import dataclass

from .altman import AltmanResult

from .piotroski import PiotroskiResult

from .beneish import BeneishResult


@dataclass(slots=True)

class BankruptcyAssessment:

    score: float

    verdict: str


class BankruptcyAnalyzer:

    @staticmethod

    def evaluate(

        altman: AltmanResult,

        piotroski: PiotroskiResult,

        beneish: BeneishResult,

    ):

        score = (

            altman.score * .45 +

            piotroski.normalized_score * .35 +

            beneish.score * .20

        )

        if score >= 80:

            verdict = "Muy saludable"

        elif score >= 65:

            verdict = "Saludable"

        elif score >= 50:

            verdict = "Precaución"

        else:

            verdict = "Riesgo elevado"

        return BankruptcyAssessment(

            score,

            verdict,

        )