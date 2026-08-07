"""Small production adapters used by the V11 composition root.

Unavailable modules are explicit N/D producers rather than fake neutral scores.
Yahoo news is exposed to the existing evidence-based sentiment engine.
"""
from __future__ import annotations

from typing import Any, Mapping


class UnavailableModule:
    """Explicitly represent a module that is not wired to a data source yet."""

    def __init__(self, name: str):
        self.name = name

    def run(self, context):
        return {
            "available": False,
            "score": None,
            "reason": f"Módulo no conectado a una fuente de producción: {self.name}",
            "evidence": [],
        }


class YahooNewsModule:
    """Fetch and normalize Yahoo/yfinance news for the V11 sentiment engine.

    yfinance has exposed two news shapes over time: a flat legacy mapping and a
    newer mapping whose fields live under ``content``. The sentiment engine
    consumes one stable schema, so normalization belongs at this provider
    boundary rather than inside the decision engine.
    """

    def __init__(self, provider_manager):
        self.provider_manager = provider_manager

    @staticmethod
    def _normalize_record(record: Mapping[str, Any]) -> dict[str, Any] | None:
        content = record.get("content")
        nested = content if isinstance(content, Mapping) else {}

        title = (
            record.get("title")
            or record.get("headline")
            or nested.get("title")
            or nested.get("headline")
            or ""
        )
        summary = (
            record.get("summary")
            or record.get("description")
            or nested.get("summary")
            or nested.get("description")
            or ""
        )
        sentiment = record.get("sentiment") or nested.get("sentiment") or ""
        published_at = (
            record.get("published_at")
            or record.get("pubDate")
            or record.get("providerPublishTime")
            or nested.get("pubDate")
            or nested.get("published_at")
            or nested.get("providerPublishTime")
            or ""
        )

        provider = record.get("source") or record.get("publisher")
        if not provider and isinstance(nested.get("provider"), Mapping):
            provider = nested["provider"].get("displayName") or nested["provider"].get("name")
        provider = provider or "yahoo"

        if not any(str(value).strip() for value in (title, summary, sentiment)):
            return None

        return {
            "title": str(title),
            "summary": str(summary),
            "sentiment": str(sentiment),
            "published_at": str(published_at) or None,
            "source": str(provider),
        }

    @classmethod
    def _normalize_news(cls, news: list[Any]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for record in news:
            if not isinstance(record, Mapping):
                continue
            item = cls._normalize_record(record)
            if item is not None:
                normalized.append(item)
        return normalized

    def run(self, context) -> dict[str, Any]:
        symbol = getattr(context.asset, "symbol", None) or ""
        response = self.provider_manager.execute_with_fallback(symbol, "get_news")
        if not response.success:
            return {
                "available": False,
                "score": None,
                "news": [],
                "reason": response.error or "No fue posible obtener noticias",
            }

        raw_news = response.data if isinstance(response.data, list) else []
        news = self._normalize_news(raw_news)
        return {
            "available": bool(news),
            "score": None,
            "news": news,
            "raw_count": len(raw_news),
            "normalized_count": len(news),
            "provider": response.provider,
            "provider_symbol": response.provider_symbol,
        }
