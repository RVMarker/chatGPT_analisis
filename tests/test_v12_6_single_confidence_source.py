from types import SimpleNamespace
from investment_analyzer.pipeline.decision_module import DecisionModule


def make_context(validation):
    return SimpleNamespace(
        fundamentals={"score":70}, valuation={"score":70,"valuation_quality":"MEDIUM"}, risk={"score":70},
        technical={"score":70}, sentiment={"score":70}, comparables={"score":70}, macro={"score":70},
        technical_result={"available":True,"requirements":{"trend":True}},
        metadata={"smart_money":{"score":70},"data_providers":{"price":"yahoo","financials":"yahoo","history":True},"provider_validation":validation},
        decision=None,
    )


def test_confidence_engine_is_single_source_of_truth():
    c=make_context({
        "ffo":{"status":"CONSISTENT","confidence":95,"vote_allowed":True},
        "net_debt":{"status":"CONSISTENT","confidence":90,"vote_allowed":True},
    })
    r=DecisionModule().run(c)
    assert r.data_coverage == 100
    assert r.confidence > 90
    assert c.metadata["confidence_result"]["coverage"] == 100


def test_conflict_changes_confidence_not_score_component_directly():
    c=make_context({
        "ffo":{"status":"CONFLICT","confidence":95,"vote_allowed":False},
        "net_debt":{"status":"CONSISTENT","confidence":90,"vote_allowed":True},
    })
    r=DecisionModule().run(c)
    assert r.data_coverage == 50
    assert r.confidence < 70
    assert any("ffo" in x.lower() for x in r.missing_factors)
