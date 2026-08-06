"""Load normalized market/financial data with provider fallback."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from investment_analyzer.common.models import FinancialStatements, PriceData, PriceHistory
from investment_analyzer.providers.provider_manager import ProviderManager
from investment_analyzer.providers.yahoo_adapter import YahooFinanceAdapter


@dataclass(slots=True)
class FinancialSnapshot:
    price: PriceData
    financials: FinancialStatements
    price_provider: str
    financials_provider: str
    price_provider_symbol: str
    financials_provider_symbol: str
    history: PriceHistory | None = None
    history_provider: str | None = None
    history_provider_symbol: str | None = None


class FinancialDataLoader:
    """Load normalized data independently, allowing price/financials/history fallback."""

    def __init__(self, provider_manager: ProviderManager | None = None, adapter=None):
        self.provider_manager = provider_manager
        self.adapter = adapter or YahooFinanceAdapter()

    def _load_yahoo(self, symbol: str):
        return self.adapter.price(symbol), self.adapter.financial_statements(symbol)

    def _load_yahoo_history(self, symbol: str):
        return self.adapter.price_history(symbol)

    def load(self, symbol: str) -> FinancialSnapshot:
        canonical = str(symbol).strip().upper()
        if not canonical:
            raise ValueError("Ticker vacío")

        if self.provider_manager is None:
            price, financials = self._load_yahoo(canonical)
            history = self._load_yahoo_history(canonical)
            return FinancialSnapshot(price, financials, "yahoo", "yahoo", canonical, canonical,
                                     history, "yahoo", canonical)

        price_response = self.provider_manager.execute_with_fallback(canonical, "get_price")
        financial_response = self.provider_manager.execute_with_fallback(canonical, "get_financial_statements")
        if not price_response.success:
            raise RuntimeError(f"No fue posible obtener precio para {canonical}: {price_response.error}")
        if not financial_response.success:
            raise RuntimeError(f"No fue posible obtener estados financieros para {canonical}: {financial_response.error}")

        price = _ensure_type(price_response.data, PriceData, "precio")
        financials = _ensure_type(financial_response.data, FinancialStatements, "estados financieros")

        history_response = self.provider_manager.execute_with_fallback(canonical, "get_price_history")
        history = None
        history_provider = None
        history_symbol = None
        if history_response.success:
            history = _ensure_type(history_response.data, PriceHistory, "histórico OHLCV")
            history_provider = history_response.provider
            history_symbol = history_response.provider_symbol or canonical

        return FinancialSnapshot(
            price=price,
            financials=financials,
            price_provider=price_response.provider,
            financials_provider=financial_response.provider,
            price_provider_symbol=price_response.provider_symbol or canonical,
            financials_provider_symbol=financial_response.provider_symbol or canonical,
            history=history,
            history_provider=history_provider,
            history_provider_symbol=history_symbol,
        )


def _ensure_type(value: Any, expected, label: str):
    if not isinstance(value, expected):
        raise TypeError(f"El provider devolvió un objeto no normalizado para {label}: {type(value).__name__}")
    return value
