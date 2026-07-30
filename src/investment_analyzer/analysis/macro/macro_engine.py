"""
Motor Macro.

El objetivo NO es predecir la economía.

Solo modificar el margen de seguridad exigido.
"""

from dataclasses import dataclass


@dataclass(slots=True)

class MacroResult:

    score: float

    required_margin: float

    explanation: str


class MacroEngine:

    @staticmethod

    def evaluate(

        risk_free_rate,

    ):

        if risk_free_rate >= .09:

            return MacroResult(

                40,

                35,

                "Tasas altas: exigir amplio margen de seguridad.",

            )

        if risk_free_rate >= .06:

            return MacroResult(

                60,

                25,

                "Entorno neutral.",

            )

        return MacroResult(

            85,

            15,

            "Tasas bajas favorecen múltiplos más elevados.",

        )