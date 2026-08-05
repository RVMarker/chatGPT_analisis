from investment_analyzer.pipeline.financial_modules import FinancialModuleAdapter


def test_financial_adapter_is_single_integration_point():
    adapter = FinancialModuleAdapter()
    assert hasattr(adapter, "integrator")
    assert hasattr(adapter, "fundamental_engine")
