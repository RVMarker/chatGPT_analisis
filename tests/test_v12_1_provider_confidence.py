from investment_analyzer.providers.provenance import DataPoint, ProvenanceValidator
from investment_analyzer.providers.provider_confidence import ProviderConfidence


def test_material_ffo_conflict_is_blocked():
    points = [
        DataPoint("ffo", 45.0, "provider_a", quality="HIGH"),
        DataPoint("ffo", 30.0, "provider_b", quality="HIGH"),
    ]
    decisions = ProviderConfidence().decide(points, ["ffo"])
    d = decisions["ffo"]
    assert d.status == "CONFLICT"
    assert d.vote_allowed is False
    assert d.value is None


def test_consistent_sources_are_allowed():
    points = [
        DataPoint("ffo", 45.0, "provider_a", quality="HIGH"),
        DataPoint("ffo", 46.0, "provider_b", quality="HIGH"),
    ]
    d = ProviderConfidence().decide(points, ["ffo"])["ffo"]
    assert d.status == "CONSISTENT"
    assert d.vote_allowed is True
    assert d.value is not None


def test_missing_field_remains_blocked():
    d = ProviderConfidence().decide([], ["affo"])["affo"]
    assert d.status == "MISSING"
    assert d.vote_allowed is False
