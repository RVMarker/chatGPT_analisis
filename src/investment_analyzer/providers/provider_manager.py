"""Provider manager with canonical/provider-specific symbol resolution."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable

from .symbol_resolver import SymbolResolver

DEFAULT_PRIORITY = ["yahoo", "fmp", "alpha_vantage", "polygon"]


@dataclass(slots=True)
class Provider:
    name: str
    enabled: bool = True
    priority: int = 99
    timeout: int = 20
    retries: int = 3
    client: Any = None


@dataclass(slots=True)
class ProviderResponse:
    provider: str
    success: bool
    latency_ms: float
    data: Any = None
    error: str | None = None
    canonical_symbol: str | None = None
    provider_symbol: str | None = None


class ProviderManager:
    def __init__(self, resolver: SymbolResolver | None = None):
        self.providers: dict[str, Provider] = {}
        self.resolver = resolver or SymbolResolver()

    def register(self, provider: Provider):
        provider.name = provider.name.strip().lower()
        self.providers[provider.name] = provider

    def register_symbol(self, canonical: str, provider: str, symbol: str):
        self.resolver.register(canonical, provider, symbol)

    def provider_symbol(self, symbol: str, provider: str) -> str:
        return self.resolver.resolve(symbol, provider).symbol

    def execute(self, provider_name: str, symbol: str, function_name: str, *args, **kwargs) -> ProviderResponse:
        provider_name = provider_name.strip().lower()
        provider = self.providers[provider_name]
        resolution = self.resolver.resolve(symbol, provider_name)
        if not provider.enabled:
            return ProviderResponse(provider_name, False, 0, error="Provider disabled",
                                    canonical_symbol=resolution.canonical, provider_symbol=resolution.symbol)
        if provider.client is None:
            return ProviderResponse(provider_name, False, 0, error="No client",
                                    canonical_symbol=resolution.canonical, provider_symbol=resolution.symbol)
        start = time.perf_counter()
        try:
            func: Callable = getattr(provider.client, function_name)
            result = func(resolution.symbol, *args, **kwargs)
            return ProviderResponse(provider_name, True, (time.perf_counter() - start) * 1000,
                                    data=result, canonical_symbol=resolution.canonical,
                                    provider_symbol=resolution.symbol)
        except Exception as ex:
            return ProviderResponse(provider_name, False, (time.perf_counter() - start) * 1000,
                                    error=str(ex), canonical_symbol=resolution.canonical,
                                    provider_symbol=resolution.symbol)

    def execute_with_fallback(self, symbol: str, function_name: str, *args, **kwargs) -> ProviderResponse:
        providers = sorted((p for p in self.providers.values() if p.enabled), key=lambda p: p.priority)
        last = None
        for provider in providers:
            response = self.execute(provider.name, symbol, function_name, *args, **kwargs)
            if response.success:
                return response
            last = response
        return last or ProviderResponse("none", False, 0, error="No enabled providers")

    def statistics(self):
        return [{"provider": p.name, "priority": p.priority, "enabled": p.enabled,
                 "timeout": p.timeout, "retries": p.retries} for p in self.providers.values()]
