from investment_analyzer.analysis.decision.decision_engine import DecisionEngine
from investment_analyzer.analysis.tactical.sentiment_engine import SentimentEngine
from investment_analyzer.analysis.tactical.smart_money_engine import SmartMoneyEngine


def test_sentiment_unavailable_is_not_neutral_50():
    result = SentimentEngine().analyze([])
    assert result.available is False
    assert result.score is None


def test_smart_money_unavailable_with_short_history():
    result = SmartMoneyEngine().analyze([])
    assert result.available is False
    assert result.score is None


def test_smart_money_proxy_uses_price_volume_evidence():
    history = [
        {"date": "2026-01-01", "close": 100, "volume": 100},
        {"date": "2026-01-02", "close": 102, "volume": 200},
    ]
    result = SmartMoneyEngine().analyze(history)
    assert result.available is True
    assert result.score == 100.0
    assert result.evidence
    assert result.evidence[0].kind == "relative_volume_pressure"


def test_missing_tactical_components_are_excluded_from_weighted_average():
    engine = DecisionEngine()
    score, breakdown, warnings = engine.tactical({
        "technical": 80,
        "sentiment": None,
        "smart_money": None,
    })
    assert score == 80.0
    assert any(x.name == "sentiment" and not x.available for x in breakdown)
    assert any(x.name == "smart_money" and not x.available for x in breakdown)
    assert all(x.weight == 1.0 for x in breakdown if x.available)
    assert warnings == []


def test_no_evidence_returns_nd_instead_of_hold():
    result = DecisionEngine().evaluate(
        strategic_scores={"fundamental": None, "valuation": None, "risk": None},
        tactical_scores={"technical": None, "sentiment": None, "smart_money": None},
        confidence_inputs={
            "provider_quality": 0,
            "freshness": 0,
            "consistency": 0,
            "completeness": 0,
            "technical_data_quality": 0,
        },
    )
    assert result.strategic_score is None
    assert result.tactical_score is None
    assert result.strategic_decision == "N/D"
    assert result.tactical_decision == "N/D"
    assert "Ningún componente disponible; veredicto N/D" in result.red_flags
