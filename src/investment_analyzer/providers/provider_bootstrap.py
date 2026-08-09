"""Application-level provider bootstrap."""
from __future__ import annotations

from .fmp_provider import FMPProvider
from .provider_manager import Provider, ProviderManager
from .provider_registry import ProviderRegistry
from .symbol_resolver import SymbolResolver
from .yahoo_provider import YahooProvider


def build_provider_stack(yahoo_provider=None, fmp_provider=None, symbol_mappings=None, security_master=None):
    """Build Registry + Manager with canonical/provider-specific symbols.

    Explicit ``symbol_mappings`` take precedence. When a SecurityMaster is
    supplied, its persisted provider identifiers are loaded automatically so
    the user-facing Yahoo ticker can differ from FMP/Polygon/etc. symbols.
    """
    resolver = SymbolResolver()

    if security_master is not None:
        for row in security_master.list_all():
            canonical = row.get("canonical_symbol")
            if not canonical:
                continue
            for provider_name in ("yahoo", "fmp", "alpha_vantage", "polygon", "finnhub"):
                provider_symbol = row.get(provider_name)
                if provider_symbol:
                    resolver.register(canonical, provider_name, provider_symbol)

    for canonical, providers in (symbol_mappings or {}).items():
        for provider_name, provider_symbol in providers.items():
            resolver.register(canonical, provider_name, provider_symbol)

    yahoo = yahoo_provider or YahooProvider()
    registry = ProviderRegistry().register_defaults(yahoo)
    manager = ProviderManager(resolver=resolver)
    manager.register(Provider(name="yahoo", priority=10, client=yahoo))

    if fmp_provider is not None:
        fmp = fmp_provider if isinstance(fmp_provider, FMPProvider) else FMPProvider(fmp_provider)
        registry.register("fmp", fmp)
        manager.register(Provider(name="fmp", priority=20, client=fmp))

    return registry, manager
