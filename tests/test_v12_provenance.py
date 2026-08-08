from investment_analyzer.providers.provenance import DataPoint, ProvenanceValidator


def test_two_sources_within_tolerance_are_consistent():
    points = [
        DataPoint("ffo", 45.41, "yahoo", "annual", quality="MEDIUM"),
        DataPoint("ffo", 44.98, "fmp", "annual", quality="HIGH"),
    ]
    result = ProvenanceValidator().validate(points, "ffo")
    assert result.status == "CONSISTENT"
    assert result.consensus_value is not None
    assert result.spread_pct < 5


def test_material_source_conflict_is_not_silently_resolved():
    points = [
        DataPoint("ffo", 45.41, "yahoo", "annual"),
        DataPoint("ffo", 31.20, "fmp", "annual"),
    ]
    result = ProvenanceValidator().validate(points, "ffo")
    assert result.status == "CONFLICT"
    assert result.consensus_value is None


def test_single_source_retains_provenance():
    result = ProvenanceValidator().validate(
        [DataPoint("affo", 0.38, "yahoo", "annual", quality="LOW_MEDIUM")], "affo"
    )
    assert result.status == "SINGLE_SOURCE"
    assert result.sources == ("yahoo",)
    assert result.confidence == 60.0
