"""
Construye el AnalysisContext.

Su objetivo es que el resto del sistema
no vuelva a usar diccionarios gigantes.
"""

from __future__ import annotations

from .analysis_context import AnalysisContext


class ContextBuilder:

    @staticmethod

    def build(

        d,

        tech,

        tech_res,

        fund,

        vi,

        proyecciones,

        sentimiento,

        riesgo,

        rendimiento,

        pivot,

        comparables,

        senales,

        estrategia,

        agentes,

        conclusion,

        dow,

        elliott,

        pe_historico,

        perfil,

        porter,

        macro,

        esg,

        est,

        backtest,

    ):

        return AnalysisContext(

            asset=d,

            technical=tech,

            technical_result=tech_res,

            fundamentals=fund,

            valuation=vi,

            dcf=vi.get(

                "dcf",

                {},

            ),

            risk=riesgo,

            comparables=comparables,

            sentiment=sentimiento,

            macro=macro,

            esg=esg,

            porter=porter,

            elliott=elliott,

            dow=dow,

            performance=rendimiento,

            pivot=pivot,

            strategy=estrategia,

            signals=senales,

            projections=proyecciones,

            agents=agentes,

            profile=perfil,

            seasonality=est,

            backtest=backtest,

            pe_history=pe_historico,

            decision=conclusion,

        )