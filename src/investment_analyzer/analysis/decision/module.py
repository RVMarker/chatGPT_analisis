"""Pipeline adapter for the V11 DecisionAnalyzer."""

from __future__ import annotations

from investment_analyzer.analysis.base import AnalysisModule
from investment_analyzer.analysis.decision.decision_analyzer import DecisionAnalyzer


class DecisionModule(AnalysisModule):
    """Convert the accumulated AnalysisContext into investment verdicts."""

    def __init__(self, analyzer: DecisionAnalyzer | None = None) -> None:
        self.analyzer = analyzer or DecisionAnalyzer()

    def run(self, context):
        result = self.analyzer.build_from_context(context)
        context.decision = result
        return result
