from types import SimpleNamespace

from investment_analyzer.pipeline.decision_report import render_decision_report


def test_reit_report_formats_payout_ratio_as_percentage_and_preserves_quality():
    context = SimpleNamespace(
        asset=SimpleNamespace(symbol="FMTY14.MX"),
        decision={
            "strategic_decision": "VENDER",
            "tactical_decision": "MANTENER",
            "strategic_score": 30.9,
            "tactical_score": 51.0,
            "strategic_coverage": 100.0,
            "tactical_coverage": 100.0,
            "confidence": 94.6,
            "data_coverage": 100.0,
            "base_confidence": 94.6,
        },
        metadata={
            "data_providers": {},
            "financial_integration": {
                "fundamental_available": True,
                "valuation_available": True,
                "risk_available": True,
            },
        },
        valuation={
            "model": "FFO_CAPITALIZATION",
            "ffo_per_share": 0.4541,
            "source_quality": "FFO_PROXY",
            "valuation_quality": "MEDIUM",
            "fair_value_per_share": 7.80,
            "margin_of_safety": -0.005,
            "affo_per_share": None,
            "distribution_per_share": 0.0465,
            "payout_ratio": 0.1024,
            "nav_per_share": None,
            "cap_rate": None,
            "net_debt_to_ebitda": None,
            "interest_coverage": None,
            "component_coverage": 0.5,
            "component_scores": {"ffo_value": 10.0, "payout": 100.0},
        },
        risk={},
        comparables={},
        macro={},
    )

    report = render_decision_report(context)

    assert "Payout / FFO           : 10.2%" in report
    assert "Payout / FFO           : 0.1%" not in report
    assert "Calidad FFO         : FFO_PROXY" in report
    assert "Calidad valoración : MEDIUM" in report
    assert "P/E                    : CONTEXTO; no vota en valoración FIBRA" in report
