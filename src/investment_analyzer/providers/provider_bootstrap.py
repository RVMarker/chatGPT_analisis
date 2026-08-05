"""Application-level provider bootstrap."""
from __future__ import annotations

from .provider_manager import Provider, ProviderManager
from .provider_registry import ProviderRegistry
from .yahoo_provider import YahooProvider


def build_provider_stack(yahoo_provider=None):
    """Build Registry + Manager without forcing optional provider SDK imports."""
    yahoo = yahoo_provider or YahooProvider()
    registry = ProviderRegistry().register_defaults(yahoo)
    manager = ProviderManager()
    manager.register(Provider(name="yahoo", priority=10, client=yahoo))
    return registry, manager
