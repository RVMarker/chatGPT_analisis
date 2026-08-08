from types import SimpleNamespace

from investment_analyzer.analysis.valuation.reit_engine import REITValuationEngine
from investment_analyzer.pipeline.decision_report import render_decision_report


def test_reit_report_recomputes_margin_and_score_from_reported_price_and_fair_value():
    context = SimpleNamespace(
        asset=SimpleNamespace(symbol="FMTY14.MX"),
        decision={
            "strategic_decision": "VENDER",
            "tactical_decision": "MANTENER",
            "strategic_score": 23.7,
            "tactical_score": 51.0,
            "strategic_coverage": 100.0,
            "tactical_coverage": 100.0,
            "confidence": 95.1,
            "data_coverage": 100.0,
            "base_confidence": 95.1,
            "strategic_breakdown": [],
            "tactical_breakdown": [],
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
            "margin_of_safety": -0.316,
            "score": 10.0,
            "decision_price": 7.84,
            "affo_per_share": None,
            "distribution_per_share": None,
            "payout_ratio": None,
            "nav_per_share": None,
            "cap_rate": None,
            "net_debt_to_ebitda": None,
            "interest_coverage": None,
            "component_coverage": 0.25,
            "component_scores": {"ffo_value": 10.0},
        },
        risk={},
        comparables={},
        macro={},
    )

    report = render_decision_report(context)

    expected_margin = 7.80 / 7.84 - 1.0
    expected_score = REITValuationEngine._score(expected_margin)

    assert f"FFO margin of safety  : {expected_margin * 100:.1f}%" in report
    assert f"Score valoración REIT : {expected_score:.1f}/100" in report
    assert "FFO margin of safety  : -31.6%" not in report
    assert "Score valoración REIT : 10.0/100" not in report
