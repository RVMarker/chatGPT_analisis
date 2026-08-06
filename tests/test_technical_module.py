from types import SimpleNamespace

from investment_analyzer.pipeline.technical_module import TechnicalModule


def test_technical_module_uses_supported_snapshot_evidence_only():
    context = SimpleNamespace(
        price=SimpleNamespace(current=110.0, previous_close=100.0, high=112.0, low=98.0),
        technical_result={},
    )
    result = TechnicalModule().run(context)
    assert result["available"] is True
    assert result["data_quality"] == "snapshot_only"
    assert result["score"] > 50
    assert "RSI" in result["history_required_for"]


def test_technical_module_does_not_fabricate_history_indicators():
    context = SimpleNamespace(
        price=SimpleNamespace(current=100.0, previous_close=None, high=None, low=None),
        technical_result={},
    )
    result = TechnicalModule().run(context)
    assert result["score"] == 50.0
    assert result["available"] is False
