"""
Altman Z-Score

Compatible con yfinance.

Utiliza únicamente información que ya descarga la V10.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AltmanResult:

    zscore: float

    classification: str

    score: float

    explanation: str


class AltmanCalculator:

    @staticmethod
    def calculate(

        working_capital,

        retained_earnings,

        ebit,

        market_value_equity,

        total_liabilities,

        sales,

        total_assets,

    ) -> AltmanResult:

        if (
            total_assets <= 0
            or total_liabilities <= 0
        ):

            return AltmanResult(

                0,

                "Datos insuficientes",

                0,

                "No fue posible calcular Altman."

            )

        A = working_capital / total_assets

        B = retained_earnings / total_assets

        C = ebit / total_assets

        D = market_value_equity / total_liabilities

        E = sales / total_assets

        z = (

            1.2 * A +

            1.4 * B +

            3.3 * C +

            0.6 * D +

            1.0 * E

        )

        if z >= 3:

            return AltmanResult(

                z,

                "Excelente",

                100,

                "Muy baja probabilidad de problemas financieros."

            )

        if z >= 2.6:

            return AltmanResult(

                z,

                "Buena",

                85,

                "Empresa financieramente saludable."

            )

        if z >= 1.8:

            return AltmanResult(

                z,

                "Zona Gris",

                60,

                "Conviene vigilar el balance."

            )

        return AltmanResult(

            z,

            "Alto Riesgo",

            20,

            "Existe riesgo financiero significativo."

        )