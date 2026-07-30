"""
Nivel de confianza del análisis.
"""

from dataclasses import dataclass


@dataclass(slots=True)

class Confidence:

    value: float

    level: str


class ConfidenceEngine:

    @staticmethod

    def evaluate(

        providers,

        freshness,

        missing,

        agreement,

    ):

        score = (

            providers * .30 +

            freshness * .25 +

            agreement * .30 +

            missing * .15

        )

        if score >= 90:

            level = "Muy Alta"

        elif score >= 80:

            level = "Alta"

        elif score >= 65:

            level = "Media"

        else:

            level = "Baja"

        return Confidence(score, level)