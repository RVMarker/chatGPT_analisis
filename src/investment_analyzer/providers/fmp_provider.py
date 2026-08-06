"""FMP provider wrapper using provider-specific identifiers."""
from __future__ import annotations

from .provider_base import ProviderBase


class FMPProvider(ProviderBase):
    NAME = "fmp"

    def __init__(self, client):
        self.client = client

    def get_price(self, symbol: str):
        return self.client.get_price(symbol)

    def get_financial_statements(self, symbol: str):
        """Return the normalized FinancialStatements object from the client."""
        if hasattr(self.client, "get_financial_statements"):
            return self.client.get_financial_statements(symbol)
        raise AttributeError("FMP client debe implementar get_financial_statements() normalizado")

    def get_balance_sheet(self, symbol: str):
        return self.client.get_balance_sheet(symbol)

    def get_income_statement(self, symbol: str):
        return self.client.get_income_statement(symbol)

    def get_cash_flow(self, symbol: str):
        return self.client.get_cash_flow(symbol)

    def get_company(self, symbol: str):
        return self.client.get_company(symbol)

    def get_news(self, symbol: str):
        return self.client.get_news(symbol)
