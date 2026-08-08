from investment_analyzer.analysis.tactical.sentiment_engine import SentimentEngine
from investment_analyzer.analysis.tactical.tactical_models import TacticalSignal
from investment_analyzer.pipeline.decision_module import DecisionModule


def test_sentiment_small_sample_is_shrunk_toward_neutral():
    result = SentimentEngine().analyze([
        {"source": "source-a", "title": "Strong growth and bullish outlook"},
    ])

    assert result.score == 80.0
    assert result.confidence == 60.0
    assert result.metadata["raw_score"] == 100.0
    assert result.metadata["sample_size"] == 1
    assert any("muestra pequeña" in warning for warning in result.warnings)


def test_sentiment_four_positive_items_is_less_extreme_than_raw_100():
    news = [
        {"source": f"source-{i}", "title": "Strong growth and bullish outlook"}
        for i in range(4)
    ]
    result = SentimentEngine().analyze(news)

    assert result.metadata["raw_score"] == 100.0
    assert result.score == 85.0
    assert result.confidence == 80.0


def test_decision_module_passes_reit_valuation_quality_to_confidence():
    class Context:
        fundamentals = {"score": 70.0}
        valuation = {"score": 20.0, "valuation_quality": "MEDIUM"}
        risk = {"score": 60.0}
        technical = {"score": 60.0}
        sentiment = {"score": 60.0}
        comparables = {"score": 50.0}
        macro = {"score": 50.0}
        metadata = {
            "smart_money": {"score": 60.0},
            "data_providers": {"price": "yahoo", "financials": "yahoo", "history": "yahoo"},
        }
        technical_result = {"available": True, "requirements": {"a": True}}

    result = DecisionModule().run(Context())
    assert result.confidence < result.base_confidence
    assert any("Calidad de valoración MEDIUM" in flag for flag in result.red_flags)
