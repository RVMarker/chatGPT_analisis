"""Altman Z-Score using fields already present in the V11 models.

The classic Z-Score formula is intended primarily for public manufacturing
companies. The engine therefore labels the result as an Altman-style signal,
not as a universal bankruptcy probability. Missing inputs are handled as
insufficient data rather than silently converted to zero.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(slots=True)
class AltmanResult:
    zscore: float | None
    classification: str
    score: float
    explanation: str
    complete: bool = True


def _number(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if isfinite(number) else None


class AltmanCalculator:
    """Calculate the classic public-company Altman Z-Score."""

    @staticmethod
    def calculate(
        working_capital: object,
        retained_earnings: object,
        ebit: object,
        market_value_equity: object,
        total_liabilities: object,
        sales: object,
        total_assets: object,
    ) -> AltmanResult:
        values = {
            "working_capital": _number(working_capital),
            "retained_earnings": _number(retained_earnings),
            "ebit": _number(ebit),
            "market_value_equity": _number(market_value_equity),
            "total_liabilities": _number(total_liabilities),
            "sales": _number(sales),
            "total_assets": _number(total_assets),
        }
        missing = [name for name, value in values.items() if value is None]
        if missing or values["total_assets"] <= 0 or values["total_liabilities"] <= 0:
            return AltmanResult(
                zscore=None,
                classification="Datos insuficientes",
                score=0.0,
                explanation="Faltan datos válidos para calcular Altman: " + ", ".join(missing),
                complete=False,
            )

        assets = values["total_assets"]
        liabilities = values["total_liabilities"]
        A = values["working_capital"] / assets
        B = values["retained_earnings"] / assets
        C = values["ebit"] / assets
        D = values["market_value_equity"] / liabilities
        E = values["sales"] / assets
        z = 1.2 * A + 1.4 * B + 3.3 * C + 0.6 * D + E

        if z >= 3.0:
            classification, score, explanation = (
                "Excelente",
                100.0,
                "Z-Score por encima de 3.0; señal financiera fuerte.",
            )
        elif z >= 2.6:
            classification, score, explanation = (
                "Buena",
                85.0,
                "Z-Score favorable, aunque requiere seguimiento.",
            )
        elif z >= 1.8:
            classification, score, explanation = (
                "Zona Gris",
                60.0,
                "Zona intermedia; conviene revisar liquidez, deuda y cobertura.",
            )
        else:
            classification, score, explanation = (
                "Alto Riesgo",
                20.0,
                "Z-Score bajo; existe señal de estrés financiero significativo.",
            )

        return AltmanResult(z, classification, score, explanation, True)
