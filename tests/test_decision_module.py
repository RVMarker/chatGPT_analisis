from investment_analyzer.pipeline.decision_module import DecisionModule


class Context:
    fundamentals = {"score": 90}
    valuation = {"score": 80}
    risk = {"score": 70}
    technical = {"score": 90}
    sentiment = {"score": 60}
    comparables = {"score": 20}
    macro = {"score": 10}
    metadata = {"data_providers": {"price": "yahoo", "financials": "yahoo"}}
    decision = None


def test_decision_module_separates_verdicts_and_context():
    result = DecisionModule().run(Context())
    assert result.strategic_score == 82.0
    assert result.tactical_score == 78.0
    assert result.strategic_decision == "COMPRAR"
    assert result.tactical_decision == "ACUMULAR"
    assert result.contextual["comparables"] == 20.0
    assert result.contextual["macro"] == 10.0
