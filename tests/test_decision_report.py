from types import SimpleNamespace

from investment_analyzer.pipeline.decision_report import render_decision_report


def test_render_decision_report_contains_verdicts_and_provider_traceability():
    context = SimpleNamespace(
        asset=SimpleNamespace(symbol="FMTY14.MX"),
        decision=SimpleNamespace(
            strategic=SimpleNamespace(verdict="COMPRAR", score=82.5),
            tactical=SimpleNamespace(verdict="ACUMULAR", score=76.0),
            confidence=84.0,
        ),
        metadata={
            "data_providers": {
                "price": "yahoo",
                "financials": "fmp",
                "price_symbol": "FMTY14.MX",
                "financials_symbol": "FMTY14",
            }
        },
        comparables={"pe": 10},
        macro={"rate": 7.5},
    )

    report = render_decision_report(context)
    assert "FMTY14.MX" in report
    assert "COMPRAR" in report
    assert "ACUMULAR" in report
    assert "82.5/100" in report
    assert "76.0/100" in report
    assert "yahoo" in report
    assert "fmp" in report
    assert "FMTY14" in report
    assert "CONTEXTO — NO VOTA DIRECTAMENTE" in report
