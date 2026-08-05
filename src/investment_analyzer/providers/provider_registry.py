"""Central provider registry.

Modules request providers from this registry instead of importing Yahoo/FMP
implementations directly.
"""
from __future__ import annotations

from typing import Dict


class ProviderRegistry:
    def __init__(self):
        self.providers: Dict[str, object] = {}

    def register(self, name: str, provider) -> None:
        key = name.strip().lower()
        if not key:
            raise ValueError("provider name vacío")
        self.providers[key] = provider

    def get(self, name: str):
        key = name.strip().lower()
        if key not in self.providers:
            raise KeyError(f"Provider no registrado: {name}")
        return self.providers[key]

    def exists(self, name: str) -> bool:
        return name.strip().lower() in self.providers

    def names(self):
        return sorted(self.providers)

    def register_defaults(self, yahoo_provider=None):
        """Register available concrete providers without importing optional SDKs."""
        if yahoo_provider is not None:
            self.register("yahoo", yahoo_provider)
        return self
