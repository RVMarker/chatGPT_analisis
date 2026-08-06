from investment_analyzer.analysis.technical.technical_module_v11 import TechnicalAnalysisV11
from investment_analyzer.common.models import PriceHistory


def history(n):
    closes = [100.0 + i * 0.1 for i in range(n)]
    return PriceHistory(
        symbol="TEST",
        dates=list(range(n)),
        open=closes,
        high=[x + 1 for x in closes],
        low=[x - 1 for x in closes],
        close=closes,
        volume=[1000.0] * n,
        interval="1d",
    )


def test_insufficient_history_is_not_neutral_50():
    result = TechnicalAnalysisV11(min_history=34).analyze(history(20))
    assert result.score is None
    assert result.metadata["available"] is False


def test_available_components_are_renormalized():
    result = TechnicalAnalysisV11().analyze(history(60))
    assert result.score is not None
    assert result.metadata["effective_weight"] > 0
    assert set(result.metadata["available_components"]).isdisjoint(result.metadata["unavailable_components"])


def test_missing_long_term_component_does_not_vote_as_50():
    result = TechnicalAnalysisV11().analyze(history(60))
    assert "long_term" in result.metadata["unavailable_components"]
    assert "long_term" not in result.metadata["component_scores"]
