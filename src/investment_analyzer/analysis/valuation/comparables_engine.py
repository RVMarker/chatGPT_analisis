"""
Comparación contra peers.

Genera un score entre 0 y 100.
"""

from dataclasses import dataclass


@dataclass(slots=True)

class ComparableResult:

    score: float

    relative_pe: float

    relative_ev: float

    explanation: str


class ComparableEngine:

    @staticmethod

    def evaluate(

        company_pe,

        peer_pe,

        company_ev,

        peer_ev,

    ):

        score = 50

        explanation = []

        relative_pe = None

        relative_ev = None

        if peer_pe > 0:

            relative_pe = company_pe / peer_pe

            if relative_pe < .8:

                score += 20

                explanation.append(

                    "P/E inferior al promedio del sector."

                )

            elif relative_pe > 1.2:

                score -= 20

                explanation.append(

                    "P/E superior al promedio."

                )

        if peer_ev > 0:

            relative_ev = company_ev / peer_ev

            if relative_ev < .8:

                score += 20

                explanation.append(

                    "EV/EBITDA con descuento."

                )

            elif relative_ev > 1.2:

                score -= 20

                explanation.append(

                    "EV/EBITDA superior al sector."

                )

        score = max(0, min(100, score))

        return ComparableResult(

            score,

            relative_pe,

            relative_ev,

            "\n".join(explanation),

        )