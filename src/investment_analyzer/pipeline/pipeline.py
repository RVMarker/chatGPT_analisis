"""
Pipeline principal del análisis.

La V10 hace todo dentro de analizar_activo().

La V11 convierte cada paso en una etapa independiente.
"""

from __future__ import annotations

from investment_analyzer.analysis.context.analysis_context import AnalysisContext


class AnalysisPipeline:

    def __init__(

        self,

        providers,

        modules,

    ):

        self.providers = providers

        self.modules = modules

    # ---------------------------------------------------------

    def run(

        self,

        ticker: str,

    ) -> AnalysisContext:

        context = AnalysisContext(

            asset=None,

        )

        context.asset = self.modules.asset.load(

            ticker,

        )

        context.technical = self.modules.technical.run(

            context,

        )

        context.fundamentals = self.modules.fundamental.run(

            context,

        )

        context.valuation = self.modules.valuation.run(

            context,

        )

        context.risk = self.modules.risk.run(

            context,

        )

        context.comparables = self.modules.comparables.run(

            context,

        )

        context.sentiment = self.modules.sentiment.run(

            context,

        )

        context.macro = self.modules.macro.run(

            context,

        )

        context.porter = self.modules.porter.run(

            context,

        )

        context.elliott = self.modules.elliott.run(

            context,

        )

        context.dow = self.modules.dow.run(

            context,

        )

        context.backtest = self.modules.backtest.run(

            context,

        )

        context.decision = self.modules.decision.run(

            context,

        )

        return context