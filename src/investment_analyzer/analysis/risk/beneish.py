"""
Beneish M-Score

Detección de posible manipulación contable.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class BeneishResult:

    m_score: float

    manipulation_risk: str

    score: float


class BeneishCalculator:

    @staticmethod
    def evaluate(

        dsri,

        gmi,

        aqi,

        sgi,

        depi,

        sgai,

        lvgi,

        tata,

    ):

        m = (

            -4.84

            + 0.92 * dsri

            + 0.528 * gmi

            + 0.404 * aqi

            + 0.892 * sgi

            + 0.115 * depi

            - 0.172 * sgai

            + 4.679 * tata

            - 0.327 * lvgi

        )

        if m < -2.22:

            return BeneishResult(

                m,

                "Bajo",

                100,

            )

        return BeneishResult(

            m,

            "Elevado",

            25,

        )