from investment_analyzer.analysis.decision.confidence_engine import ConfidenceEngine


def test_coverage_counts_only_usable_evidence():
    result = ConfidenceEngine().evaluate(
        ["ffo", "affo", "net_debt", "ebitda"],
        {
            "ffo": {"status":"CONSISTENT", "confidence":95, "vote_allowed":True},
            "affo": {"status":"MISSING", "confidence":0, "vote_allowed":False},
            "net_debt": {"status":"CONFLICT", "confidence":90, "vote_allowed":False},
            "ebitda": {"status":"CONSISTENT", "confidence":90, "vote_allowed":True},
        },
    )
    assert result.coverage == 50.0
    assert result.usable == 2
    assert "net_debt" in result.blocked
    assert "affo" in result.missing


def test_empty_evidence_has_zero_confidence():
    result = ConfidenceEngine().evaluate(["ffo"], {})
    assert result.coverage == 0
    assert result.confidence == 0
