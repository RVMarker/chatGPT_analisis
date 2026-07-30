"""
provider_registry.py

Registro central de proveedores.

Todos los módulos pedirán datos al registry,
nunca directamente a Yahoo o FMP.
"""

from __future__ import annotations

from typing import Dict


class ProviderRegistry:

    def __init__(self):

        self.providers: Dict[str, object] = {}

    # ---------------------------------------------------------

    def register(

        self,

        name: str,

        provider,

    ):

        self.providers[name.lower()] = provider

    # ---------------------------------------------------------

    def get(

        self,

        name: str,

    ):

        return self.providers[name.lower()]

    # ---------------------------------------------------------

    def exists(

        self,

        name: str,

    ):

        return name.lower() in self.providers

    # ---------------------------------------------------------

    def names(self):

        return list(self.providers.keys())