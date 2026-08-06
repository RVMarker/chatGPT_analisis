"""ProviderBase-compatible wrapper around YahooFinanceAdapter."""
from __future__ import annotations

from .provider_base import ProviderBase
from .yahoo_adapter import YahooFinanceAdapter


class YahooProvider(ProviderBase):
    NAME = "yahoo"

    def __init__(self, adapter=None):
        self.adapter = adapter or YahooFinanceAdapter()

    def get_price(self, symbol: str):
        return self.adapter.price(symbol)

    def get_price_history(self, symbol: str):
        return self.adapter.price_history(symbol)

    def get_financial_statements(self, symbol: str):
        return self.adapter.financial_statements(symbol)

    def get_balance_sheet(self, symbol: str):
        return self.adapter.financial_statements(symbol).balance

    def get_income_statement(self, symbol: str):
        return self.adapter.financial_statements(symbol).income

    def get_cash_flow(self, symbol: str):
        return self.adapter.financial_statements(symbol).cashflow

    def get_company(self, symbol: str):
        ticker = self.adapter._ticker(symbol)
        return getattr(ticker, "info", {}) or {}

    def get_news(self, symbol: str):
        ticker = self.adapter._ticker(symbol)
        return getattr(ticker, "news", []) or []
