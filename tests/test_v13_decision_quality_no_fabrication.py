from types import SimpleNamespace

from investment_analyzer.pipeline.decision_module import DecisionModule


def test_data_quality_does_not_invent_freshness_or_consistency():
    context = SimpleNamespace(
        metadata={"data_providers": {"price": "provider-a", "financials": "provider-b", "history": "provider-c"}},
        technical_result={"available": True, "requirements": {"rsi": True, "macd": False}},
        fundamentals=None,
        valuation=None,
        risk=None,
        technical=None,
        sentiment=None,
        comparables=None,
        macro=None,
    )
    result = DecisionModule._data_quality_inputs(context)
    assert result["provider_quality"] == 100.0
    assert result["completeness"] == 100.0
    assert result["freshness"] is None
    assert result["consistency"] is None
    assert result["technical_data_quality"] == 50.0
