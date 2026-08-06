from investment_analyzer.app import build_application
from investment_analyzer.pipeline.production_modules import UnavailableModule, YahooNewsModule


def test_build_application_wires_a_runnable_pipeline_factory():
    pipeline, manager, registry = build_application()

    assert pipeline.providers is manager
    assert pipeline.financial_loader.provider_manager is manager
    assert isinstance(pipeline.modules.comparables, UnavailableModule)
    assert isinstance(pipeline.modules.macro, UnavailableModule)
    assert isinstance(pipeline.modules.sentiment, YahooNewsModule)
    assert registry is not None


def test_unavailable_production_module_returns_nd_instead_of_raising():
    module = UnavailableModule("macro")
    result = module.run(object())

    assert result["available"] is False
    assert result["score"] is None
