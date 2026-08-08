from investment_analyzer.analysis.data_quality.reit_gate import REITDataQualityGate


def test_reit_gate_keeps_missing_metrics_as_missing_and_does_not_invent_them():
    result = REITDataQualityGate().validate(
        {
            "ffo": 45.41,
            "affo": None,
            "distribution": None,
            "net_debt": 500,
            "ebitda": 100,
            "interest_expense": 40,
            "property_value": None,
            "shares_outstanding": 100,
            "debt_equity": 17.04,
        },
        asset_type="FIBRA",
        source="yahoo",
    )
    assert result.passed is True
    assert "affo" in result.missing
    assert "distribution" in result.missing
    assert "property_value" in result.missing
    assert result.evidence["debt_equity"].role == "CONTEXT"
    assert result.evidence["debt_equity"].notes.startswith("Para FIBRA")


def test_reit_gate_blocks_unverified_distribution_from_vote():
    result = REITDataQualityGate().validate(
        {
            "ffo": 45.41,
            "affo": 40,
            "distribution": 20,
            "net_debt": 500,
            "ebitda": 100,
            "interest_expense": 40,
            "property_value": 1000,
            "shares_outstanding": 100,
        },
        asset_type="FIBRA",
        source="yahoo",
        verified_fields={"ffo", "net_debt", "ebitda", "interest_expense", "shares_outstanding"},
        field_quality={"distribution": "LOW"},
    )
    assert "distribution" in result.blocked_from_vote
    assert result.evidence["distribution"].role == "VOTE_IF_VERIFIED"


def test_reit_gate_requires_ffo_and_shares_to_pass_minimum_valuation_gate():
    result = REITDataQualityGate().validate(
        {"ffo": None, "shares_outstanding": 100},
        asset_type="FIBRA",
    )
    assert result.passed is False
    assert "ffo" in result.missing
