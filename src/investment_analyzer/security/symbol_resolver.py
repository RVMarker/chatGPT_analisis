"""
symbol_resolver.py

Investment Analyzer v11

Responsabilidades

- Resolver cualquier identificador recibido por el usuario.
- Buscar en SecurityMaster.
- Si no existe, inferir proveedor.
- Normalizar el ticker.
- Registrar automáticamente el activo.
"""

from __future__ import annotations

import re

from security_master import (
    Security,
    SecurityMaster,
)


class SymbolResolver:

    def __init__(

        self,

        security_master: SecurityMaster,

    ):

        self.security_master = security_master

    # ---------------------------------------------------------

    def normalize(

        self,

        symbol: str,

    ) -> str:

        symbol = symbol.strip()

        symbol = symbol.upper()

        symbol = symbol.replace(" ", "")

        return symbol

    # ---------------------------------------------------------

    def is_isin(

        self,

        text: str,

    ) -> bool:

        return bool(

            re.match(

                r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$",

                text,

            )

        )

    # ---------------------------------------------------------

    def resolve(

        self,

        text: str,

    ) -> Security | None:

        text = self.normalize(text)

        security = self.security_master.get(text)

        if security is not None:

            return security

        return None

    # ---------------------------------------------------------

    def provider_symbol(

        self,

        text: str,

        provider: str,

    ) -> str:

        security = self.resolve(text)

        if security is None:

            return self.normalize(text)

        return self.security_master.provider_symbol(

            security.canonical_symbol,

            provider,

        )

    # ---------------------------------------------------------

    def ensure(

        self,

        symbol: str,

    ) -> Security:

        security = self.resolve(symbol)

        if security:

            return security

        normalized = self.normalize(symbol)

        security = Security(

            asset_id=f"TMP-{normalized}",

            canonical_symbol=normalized,

            name=normalized,

            exchange="UNKNOWN",

            currency="UNKNOWN",

            asset_type="UNKNOWN",

            yahoo=normalized,

        )

        self.security_master.add(security)

        return security