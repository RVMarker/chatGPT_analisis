from types import SimpleNamespace

from investment_analyzer.analysis.data_quality.reit_gate import REITDataQualityGate


def test_reit_gate_marks_debt_equity_as_context_and_missing_affo_as_blocked():
    result = REITDataQualityGate().validate(
        {
            "ffo": 45.41,
            "affo": None,
            "distribution": None,
            "net_debt": 100.0,
            "ebitda": 20.0,
            "interest_expense": 5.0,
            "property_value": None,
            "shares_outstanding": 100.0,
            "debt_equity": 17.04,
        },
        asset_type="FIBRA",
        source="yahoo",
        fiscal_date="2026-06-30",
    )
    assert result.passed is True
    assert result.evidence["debt_equity"].role == "CONTEXT"
    assert "affo" in result.missing
    assert "property_value" in result.missing


def test_reit_gate_fails_without_ffo_or_shares():
    result = REITDataQualityGate().validate(
        {"ffo": None, "shares_outstanding": None},
        asset_type="FIBRA",
    )
    assert result.passed is False
    assert "ffo" in result.blocked_from_vote
    assert "shares_outstanding" in result.blocked_from_vote
