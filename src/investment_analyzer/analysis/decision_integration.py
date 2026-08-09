"""V12.43 specialized score integration without double counting."""
from __future__ import annotations
from typing import Any

class SpecializedDecisionIntegrator:
    def integrate(self, *, asset_type: str, strategic: dict[str, Any], specialized: dict[str, Any] | None = None) -> dict[str, Any]:
        specialized = specialized or {}
        if asset_type != "ETF" or "etf" not in specialized:
            return strategic
        etf = specialized["etf"]
        score = etf.get("score")
        coverage = float(etf.get("coverage", 0) or 0)
        if score is None:
            return strategic
        # ETF score becomes the strategic ETF-specific component; it is not added
        # on top of the same raw fields, avoiding double counting.
        base = dict(strategic)
        previous = base.get("score")
        base["generic_score"] = previous
        base["score"] = round(float(score), 2)
        base["specialized_component"] = "ETF"
        base["specialized_score"] = round(float(score), 2)
        base["specialized_coverage"] = round(coverage, 2)
        base["decision_basis"] = "ETF-specific strategic score"
        return base
