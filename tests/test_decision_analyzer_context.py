from dataclasses import dataclass

from investment_analyzer.analysis.decision.decision_analyzer import DecisionAnalyzer


@dataclass
class EngineResult:
    score: float
    strengths: list[str]
    red_flags: list[str]


@dataclass
class Asset:
    smart_money_score: float = 75
    provider_quality: float = 95
    data_freshness: float = 90
    provider_consistency: float = 85
    completeness: float = 92


class Context:
    asset = Asset()
    fundamentals = EngineResult(80, ["ROIC fuerte"], [])
    valuation = EngineResult(90, [], [])
    dcf = {}
    risk = EngineResult(75, ["Balance sólido"], [])
    technical = EngineResult(70, [], [])
    sentiment = EngineResult(65, [], [])
    comparables = EngineResult(10, [], [])
    macro = EngineResult(5, [], [])


def test_dataclass_results_are_consumed_and_context_does_not_vote():
    result = DecisionAnalyzer().build_from_context(Context())
    assert result["strategic"]["score"] == 83
    assert result["tactical"]["score"] == 70
    assert result["strategic"]["decision"] == "COMPRAR"
    assert result["tactical"]["decision"] == "ACUMULAR"
    assert result["contextual"] == {"comparables": 10.0, "macro": 5.0}
    assert "ROIC fuerte" in result["strengths"]
    assert "Balance sólido" in result["strengths"]
