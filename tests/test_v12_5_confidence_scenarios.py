from investment_analyzer.analysis.decision.confidence_engine import ConfidenceEngine


def test_full_consistent_evidence_is_high_confidence():
    fields=["ffo","affo","net_debt","ebitda"]
    validation={f:{"status":"CONSISTENT","confidence":95,"vote_allowed":True} for f in fields}
    r=ConfidenceEngine().evaluate(fields, validation)
    assert r.coverage == 100
    assert r.confidence >= 95


def test_conflict_does_not_reduce_score_directly_but_reduces_confidence():
    fields=["ffo","net_debt"]
    validation={"ffo":{"status":"CONSISTENT","confidence":95,"vote_allowed":True},"net_debt":{"status":"CONFLICT","confidence":95,"vote_allowed":False}}
    r=ConfidenceEngine().evaluate(fields, validation)
    assert r.coverage == 50
    assert r.confidence < 70
