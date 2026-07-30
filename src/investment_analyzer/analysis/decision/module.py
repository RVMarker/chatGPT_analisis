"""
Wrapper del Decision Engine.

Hace compatible el nuevo motor con el pipeline.
"""

from __future__ import annotations

from investment_analyzer.analysis.base import AnalysisModule

from investment_analyzer.analysis.decision.decision_analyzer import (

    DecisionAnalyzer,

)


class DecisionModule(

    AnalysisModule,

):

    def __init__(self):

        self.engine = DecisionAnalyzer()

    def run(

        self,

        context,

    ):

        return self.engine.build(

            fundamental_score=context.fundamentals["score"],

            dcf_score=context.valuation["score"],

            comparables_score=context.comparables["score"],

            macro_score=context.macro["score"],

            risk_score=context.risk["score"],

            technical_score=context.technical["score"],

            sentiment_score=context.sentiment["score"],

            smart_money_score=context.asset.smart_money_score,

            provider_quality=context.asset.provider_quality,

            freshness=context.asset.data_freshness,

            consistency=context.asset.provider_consistency,

            completeness=context.asset.completeness,

            strengths=context.risk["strengths"],

            red_flags=context.risk["red_flags"],

            counter_thesis=context.risk["counter_thesis"],

        )