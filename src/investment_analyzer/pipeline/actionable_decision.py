"""V12.8 final actionable decision adapter."""
from __future__ import annotations
from dataclasses import asdict
from investment_analyzer.analysis.decision.action_policy import ActionPolicyEngine

class ActionableDecisionAdapter:
    def __init__(self, policy=None):
        self.policy = policy or ActionPolicyEngine()

    @staticmethod
    def _get(obj, name, default=None):
        if isinstance(obj, dict): return obj.get(name, default)
        return getattr(obj, name, default)

    def apply(self, result):
        strategic=self._get(result,"strategic",{}) or {}
        tactical=self._get(result,"tactical",{}) or {}
        confidence=float(self._get(result,"confidence",0) or 0)
        coverage=float(self._get(result,"data_coverage",0) or 0)
        strategic_score=self._get(strategic,"score")
        tactical_score=self._get(tactical,"score")
        strategic_verdict=self._get(strategic,"verdict","N/D")
        tactical_verdict=self._get(tactical,"verdict","N/D")
        strategic_policy=self.policy.evaluate(strategic_verdict, strategic_score, confidence, coverage)
        tactical_policy=self.policy.evaluate(tactical_verdict, tactical_score, confidence, coverage)
        payload={"strategic":asdict(strategic_policy),"tactical":asdict(tactical_policy),"confidence":confidence,"coverage":coverage}
        if hasattr(result,"actionable"): result.actionable=payload
        else:
            try: result.actionable=payload
            except Exception: pass
        return result
