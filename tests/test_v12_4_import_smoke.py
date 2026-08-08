"""V12.4 import/API smoke tests: catches integration-time import breakage."""

def test_v12_modules_import():
    from investment_analyzer.providers.provenance import DataPoint, ProvenanceValidator
    from investment_analyzer.providers.provider_confidence import ProviderConfidence
    from investment_analyzer.pipeline.decision_module import DecisionModule
    from investment_analyzer.analysis.integration.fundamental_valuation_risk import FinancialAnalysisIntegrator
    assert DataPoint and ProvenanceValidator and ProviderConfidence and DecisionModule and FinancialAnalysisIntegrator


def test_provider_confidence_api_is_stable():
    from investment_analyzer.providers.provenance import DataPoint
    from investment_analyzer.providers.provider_confidence import ProviderConfidence
    result = ProviderConfidence().decide([DataPoint("ffo", 10.0, "test", quality="HIGH")], ["ffo"])
    assert result["ffo"].field == "ffo"
    assert result["ffo"].value == 10.0
    assert result["ffo"].vote_allowed is True
