"""Small production adapters used by the V11 composition root.

Unavailable modules are explicit N/D producers rather than fake neutral scores.
Yahoo news is exposed to the existing evidence-based sentiment engine.
"""
from __future__ import annotations

from typing import Any


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
    """Fetch Yahoo news through the already configured provider manager."""

    def __init__(self, provider_manager):
        self.provider_manager = provider_manager

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
        news = response.data if isinstance(response.data, list) else []
        return {
            "available": bool(news),
            "score": None,
            "news": news,
            "provider": response.provider,
            "provider_symbol": response.provider_symbol,
        }
