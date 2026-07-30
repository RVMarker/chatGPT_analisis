"""
Piotroski F-Score

Investment Analyzer v11
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PiotroskiResult:

    score: int

    normalized_score: float

    explanation: str


class PiotroskiCalculator:

    @staticmethod
    def calculate(

        roa_positive: bool,

        operating_cf_positive: bool,

        roa_improved: bool,

        cfo_gt_net_income: bool,

        leverage_decreased: bool,

        current_ratio_improved: bool,

        no_new_shares: bool,

        gross_margin_improved: bool,

        asset_turnover_improved: bool,

    ) -> PiotroskiResult:

        score = sum(

            [

                roa_positive,

                operating_cf_positive,

                roa_improved,

                cfo_gt_net_income,

                leverage_decreased,

                current_ratio_improved,

                no_new_shares,

                gross_margin_improved,

                asset_turnover_improved,

            ]

        )

        normalized = score * (100 / 9)

        if score >= 8:

            txt = "Excelente calidad financiera."

        elif score >= 6:

            txt = "Empresa sólida."

        elif score >= 4:

            txt = "Calidad aceptable."

        else:

            txt = "Calidad financiera débil."

        return PiotroskiResult(

            score,

            normalized,

            txt,

        )