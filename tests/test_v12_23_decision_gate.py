from investment_analyzer.analysis.decision.consensus_decision_gate import ConsensusDecisionGate

def test_conflict_blocks_decision_and_reduces_score():
    g=ConsensusDecisionGate().evaluate({"ffo":[("yahoo",.45),("provider_b",.60)],"price":[("yahoo",14.2),("provider_b",14.25)]},critical_fields=["ffo","price"])
    assert g.decision_allowed is False
    assert "ffo" in g.blocked_fields
    assert g.coverage_pct < 100
    assert ConsensusDecisionGate.protect_score(20,g) > 20
    assert ConsensusDecisionGate.protect_verdict("VENDER",g)=="MANTENER"

def test_agreement_passes_gate():
    g=ConsensusDecisionGate().evaluate({"ffo":[("a",.450),("b",.452)],"price":[("a",14.20),("b",14.25)]},critical_fields=["ffo","price"])
    assert g.decision_allowed is True
    assert g.coverage_pct == 100
