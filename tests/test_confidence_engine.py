"""Regression tests for confidence scoring semantics."""

from investment_analyzer.analysis.confidence.confidence import ConfidenceEngine


def test_no_missing_data_does_not_penalize_confidence():
    result = ConfidenceEngine.evaluate(
        providers=100,
        freshness=100,
        missing=0,
        agreement=100,
    )
    assert result.value == 100
    assert result.level == "Muy Alta"


def test_missing_data_reduces_confidence():
    result = ConfidenceEngine.evaluate(
        providers=100,
        freshness=100,
        missing=100,
        agreement=100,
    )
    assert result.value == 85
    assert result.level == "Alta"


def test_confidence_inputs_are_bounded():
    result = ConfidenceEngine.evaluate(
        providers=150,
        freshness=-10,
        missing=0,
        agreement=100,
    )
    assert result.value == 70
