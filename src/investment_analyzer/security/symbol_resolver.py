"""Resolve the user's Yahoo-style ticker to provider-specific symbols.

The user-facing symbol remains exactly the Yahoo Finance symbol. Provider
mappings are stored in SecurityMaster, so FMP/Alpha Vantage/etc. never need
to share Yahoo's nomenclature.
"""

from __future__ import annotations

import re

from .security_master import Security, SecurityMaster


class SymbolResolver:
    def __init__(self, security_master: SecurityMaster) -> None:
        self.security_master = security_master

    @staticmethod
    def normalize(symbol: str) -> str:
        return symbol.strip().upper().replace(" ", "")

    @staticmethod
    def is_isin(text: str) -> bool:
        return bool(re.fullmatch(r"[A-Z]{2}[A-Z0-9]{9}[0-9]", text.upper()))

    def resolve(self, text: str) -> Security | None:
        return self.security_master.get(self.normalize(text))

    def provider_symbol(self, text: str, provider: str) -> str:
        security = self.resolve(text)
        if security is None:
            return self.normalize(text)
        return self.security_master.provider_symbol(
            security.canonical_symbol,
            provider,
        )

    def ensure(self, symbol: str) -> Security:
        normalized = self.normalize(symbol)
        security = self.resolve(normalized)
        if security is not None:
            return security

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
