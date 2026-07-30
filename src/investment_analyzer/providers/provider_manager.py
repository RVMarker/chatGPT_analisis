"""
provider_manager.py
Investment Analyzer v11

Administrador de proveedores de datos.

Responsabilidades

- Resolver el símbolo correcto para cada proveedor.
- Administrar prioridades.
- Fallback automático.
- Medir tiempos.
- Unificar respuestas.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable


# ============================================================
# CONFIG
# ============================================================

DEFAULT_PRIORITY = [
    "yahoo",
    "fmp",
    "alpha_vantage",
    "polygon",
]


# ============================================================
# PROVIDER
# ============================================================

@dataclass(slots=True)
class Provider:

    name: str

    enabled: bool = True

    priority: int = 99

    timeout: int = 20

    retries: int = 3

    client: Any = None


# ============================================================
# SYMBOL MAP
# ============================================================

class SymbolMapper:
    """
    Convierte un ticker "interno" al ticker
    que utiliza cada proveedor.

    Ejemplo

    Interno:
        FMTY14.MX

    Yahoo:
        FMTY14.MX

    FMP:
        FMTY14

    Polygon:
        FMTY14
    """

    def __init__(self):

        self.mapping: dict[str, dict[str, str]] = {}

    def register(

        self,

        canonical: str,

        provider: str,

        symbol: str,

    ):

        self.mapping.setdefault(canonical.upper(), {})

        self.mapping[canonical.upper()][provider] = symbol

    def resolve(

        self,

        canonical: str,

        provider: str,

    ) -> str:

        canonical = canonical.upper()

        if canonical not in self.mapping:

            return canonical

        return self.mapping[canonical].get(provider, canonical)


# ============================================================
# RESULT
# ============================================================

@dataclass(slots=True)
class ProviderResponse:

    provider: str

    success: bool

    latency_ms: float

    data: Any = None

    error: str | None = None


# ============================================================
# PROVIDER MANAGER
# ============================================================

class ProviderManager:

    def __init__(self):

        self.providers: dict[str, Provider] = {}

        self.mapper = SymbolMapper()

    # --------------------------------------------------------

    def register(

        self,

        provider: Provider,

    ):

        self.providers[provider.name] = provider

    # --------------------------------------------------------

    def provider_symbol(

        self,

        symbol: str,

        provider: str,

    ) -> str:

        return self.mapper.resolve(

            symbol,

            provider,

        )

    # --------------------------------------------------------

    def execute(

        self,

        provider_name: str,

        symbol: str,

        function_name: str,

        *args,

        **kwargs,

    ) -> ProviderResponse:

        provider = self.providers[provider_name]

        if not provider.enabled:

            return ProviderResponse(

                provider=provider_name,

                success=False,

                latency_ms=0,

                error="Provider disabled",

            )

        client = provider.client

        if client is None:

            return ProviderResponse(

                provider=provider_name,

                success=False,

                latency_ms=0,

                error="No client",

            )

        symbol = self.provider_symbol(

            symbol,

            provider_name,

        )

        start = time.perf_counter()

        try:

            func: Callable = getattr(

                client,

                function_name,

            )

            result = func(

                symbol,

                *args,

                **kwargs,

            )

            elapsed = (

                time.perf_counter()

                - start

            ) * 1000

            return ProviderResponse(

                provider=provider_name,

                success=True,

                latency_ms=elapsed,

                data=result,

            )

        except Exception as ex:

            elapsed = (

                time.perf_counter()

                - start

            ) * 1000

            return ProviderResponse(

                provider=provider_name,

                success=False,

                latency_ms=elapsed,

                error=str(ex),

            )

    # --------------------------------------------------------

    def execute_with_fallback(

        self,

        symbol: str,

        function_name: str,

        *args,

        **kwargs,

    ) -> ProviderResponse:

        providers = sorted(

            self.providers.values(),

            key=lambda p: p.priority,

        )

        last = None

        for provider in providers:

            response = self.execute(

                provider.name,

                symbol,

                function_name,

                *args,

                **kwargs,

            )

            if response.success:

                return response

            last = response

        return last

    # --------------------------------------------------------

    def statistics(self):

        table = []

        for provider in self.providers.values():

            table.append(

                {

                    "provider": provider.name,

                    "priority": provider.priority,

                    "enabled": provider.enabled,

                    "timeout": provider.timeout,

                    "retries": provider.retries,

                }

            )

        return table


# ============================================================
# EXAMPLE
# ============================================================

if __name__ == "__main__":

    pm = ProviderManager()

    pm.mapper.register(

        canonical="FMTY14.MX",

        provider="fmp",

        symbol="FMTY14",

    )

    pm.mapper.register(

        canonical="FMTY14.MX",

        provider="polygon",

        symbol="FMTY14",

    )

    print(

        pm.provider_symbol(

            "FMTY14.MX",

            "fmp",

        )

    )

    print(

        pm.provider_symbol(

            "FMTY14.MX",

            "yahoo",

        )

    )