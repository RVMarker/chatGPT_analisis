from investment_analyzer.providers.provenance import DataPoint
from investment_analyzer.providers.provider_confidence import ProviderConfidence


def test_conflicting_ffo_is_blocked_before_reit_valuation():
    points = [DataPoint("ffo", 45.0, "a", quality="HIGH"), DataPoint("ffo", 20.0, "b", quality="HIGH")]
    d = ProviderConfidence().decide(points, ["ffo"])["ffo"]
    assert d.status == "CONFLICT"
    assert not d.vote_allowed


def test_consistent_ffo_can_reach_valuation():
    points = [DataPoint("ffo", 45.0, "a", quality="HIGH"), DataPoint("ffo", 46.0, "b", quality="HIGH")]
    d = ProviderConfidence().decide(points, ["ffo"])["ffo"]
    assert d.status == "CONSISTENT"
    assert d.vote_allowed
    assert 45.0 <= d.value <= 46.0
