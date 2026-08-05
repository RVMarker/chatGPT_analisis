"""Canonical Asset loader for V11.

The user-facing symbol is the Yahoo Finance symbol. Provider-specific symbols
remain inside SecurityMaster and are never substituted into Asset.symbol.
"""
from __future__ import annotations

from investment_analyzer.security.asset import Asset
from investment_analyzer.security.company import Company
from investment_analyzer.security.exchange import Exchange
from investment_analyzer.security.identifier import SecurityIdentifier
from investment_analyzer.security.security_master import SecurityMaster


class AssetLoader:
    def __init__(self, security_master: SecurityMaster | None = None):
        self.security_master = security_master or SecurityMaster()

    @staticmethod
    def _canonical(symbol: str) -> str:
        value = (symbol or "").strip().upper()
        if not value:
            raise ValueError("Ticker vacío")
        return value

    def load(self, symbol: str) -> Asset:
        canonical = self._canonical(symbol)
        security = self.security_master.get(canonical)

        if security is None:
            # Unknown symbols remain usable as Yahoo symbols. Other providers
            # must resolve their own identifier instead of guessing here.
            return Asset(
                asset_id=f"YAHOO:{canonical}",
                symbol=canonical,
                asset_type="UNKNOWN",
                currency="USD",
                company=Company(name=canonical),
                exchange=Exchange(code="UNKNOWN", name="Unknown", country="", currency="USD", timezone="UTC"),
                identifiers=SecurityIdentifier(ticker=canonical, yahoo=canonical),
            )

        return Asset(
            asset_id=security.asset_id,
            symbol=security.canonical_symbol,
            asset_type=security.asset_type,
            currency=security.currency,
            company=Company(name=security.name),
            exchange=Exchange(code=security.exchange, name=security.exchange, country="", currency=security.currency, timezone="UTC"),
            identifiers=SecurityIdentifier(
                ticker=security.canonical_symbol,
                yahoo=security.yahoo,
                fmp=security.fmp,
                alpha_vantage=security.alpha_vantage,
                polygon=security.polygon,
                finnhub=security.finnhub,
                isin=security.isin,
                figi=security.figi,
            ),
        )
