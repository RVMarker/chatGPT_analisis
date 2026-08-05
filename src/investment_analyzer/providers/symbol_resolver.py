"""Provider-aware symbol resolution for V11.

The canonical ticker is never mutated. Each provider receives its own
identifier, with an explicit mapping taking precedence over heuristics.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SymbolResolution:
    canonical: str
    provider: str
    symbol: str
    source: str


class SymbolResolver:
    def __init__(self):
        self._mapping: dict[str, dict[str, str]] = {}

    def register(self, canonical: str, provider: str, symbol: str) -> None:
        canonical = self.normalize(canonical)
        provider = provider.strip().lower()
        symbol = symbol.strip()
        if not symbol:
            raise ValueError("provider symbol vacío")
        self._mapping.setdefault(canonical, {})[provider] = symbol

    @staticmethod
    def normalize(symbol: str) -> str:
        value = str(symbol).strip().upper()
        if not value:
            raise ValueError("ticker vacío")
        return value

    def resolve(self, canonical: str, provider: str) -> SymbolResolution:
        canonical = self.normalize(canonical)
        provider = provider.strip().lower()
        explicit = self._mapping.get(canonical, {}).get(provider)
        if explicit:
            return SymbolResolution(canonical, provider, explicit, "explicit_mapping")
        return SymbolResolution(canonical, provider, canonical, "canonical_fallback")

    def mappings_for(self, canonical: str) -> dict[str, str]:
        return dict(self._mapping.get(self.normalize(canonical), {}))
