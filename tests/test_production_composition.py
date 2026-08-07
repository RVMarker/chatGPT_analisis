from types import SimpleNamespace

from investment_analyzer.app import build_application
from investment_analyzer.pipeline.production_modules import UnavailableModule, YahooNewsModule
from investment_analyzer.pipeline.comparables_production import ProductionComparablesModule


def test_build_application_wires_a_runnable_pipeline_factory():
    pipeline, manager, registry = build_application()

    assert pipeline.providers is manager
    assert pipeline.financial_loader.provider_manager is manager
    assert isinstance(pipeline.modules.comparables, ProductionComparablesModule)
    assert isinstance(pipeline.modules.macro, UnavailableModule)
    assert isinstance(pipeline.modules.sentiment, YahooNewsModule)
    assert registry is not None


def test_unavailable_production_module_returns_nd_instead_of_raising():
    module = UnavailableModule("macro")
    result = module.run(object())

    assert result["available"] is False
    assert result["score"] is None


def test_yahoo_news_normalizes_current_nested_yfinance_shape():
    raw = [
        {
            "id": "1",
            "content": {
                "title": "FMTY reports strong growth and upgrade",
                "summary": "Operating results beat expectations.",
                "pubDate": "2026-08-07T10:00:00Z",
                "provider": {"displayName": "Yahoo Finance"},
            },
        }
    ]

    manager = SimpleNamespace(
        execute_with_fallback=lambda symbol, operation: SimpleNamespace(
            success=True,
            data=raw,
            provider="yahoo",
            provider_symbol=symbol,
            error=None,
        )
    )
    module = YahooNewsModule(manager)
    context = SimpleNamespace(asset=SimpleNamespace(symbol="FMTY14.MX"))

    result = module.run(context)

    assert result["available"] is True
    assert result["raw_count"] == 1
    assert result["normalized_count"] == 1
    assert result["news"][0]["title"].startswith("FMTY reports strong growth")
    assert result["news"][0]["summary"] == "Operating results beat expectations."
    assert result["news"][0]["source"] == "Yahoo Finance"
    assert result["news"][0]["published_at"] == "2026-08-07T10:00:00Z"


def test_yahoo_news_discards_unusable_records_without_fabricating_sentiment():
    raw = [
        {"content": {"title": "", "summary": ""}},
        {"content": {"title": "Market update", "summary": "No directional information."}},
    ]

    manager = SimpleNamespace(
        execute_with_fallback=lambda symbol, operation: SimpleNamespace(
            success=True,
            data=raw,
            provider="yahoo",
            provider_symbol=symbol,
            error=None,
        )
    )
    module = YahooNewsModule(manager)
    context = SimpleNamespace(asset=SimpleNamespace(symbol="FMTY14.MX"))

    result = module.run(context)

    assert result["raw_count"] == 2
    assert result["normalized_count"] == 1
    assert result["news"][0]["title"] == "Market update"
