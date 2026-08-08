from types import SimpleNamespace
from investment_analyzer.pipeline.decision_module import DecisionModule


def context_with_validation(validation):
    return SimpleNamespace(
        fundamentals={"score":70}, valuation={"score":70,"valuation_quality":"MEDIUM"}, risk={"score":70},
        technical={"score":70}, sentiment={"score":70}, comparables={"score":70}, macro={"score":70},
        technical_result={"available":True,"requirements":{"trend":True}},
        metadata={"smart_money":{"score":70},"data_providers":{"price":"yahoo","financials":"yahoo","history":True},"provider_validation":validation},
        decision=None,
    )


def test_conflict_lowers_confidence_and_is_missing_factor():
    context=context_with_validation({"ffo":{"status":"CONFLICT","confidence":90,"vote_allowed":False}})
    result=DecisionModule().run(context)
    assert result.confidence <= 60
    assert any("ffo" in x.lower() for x in result.missing_factors)


def test_consistent_provenance_does_not_force_confidence_penalty():
    context=context_with_validation({"ffo":{"status":"CONSISTENT","confidence":95,"vote_allowed":True}})
    result=DecisionModule().run(context)
    assert result.confidence > 60
