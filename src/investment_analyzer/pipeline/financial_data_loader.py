"""Load normalized market/financial data with provider fallback."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from investment_analyzer.common.models import FinancialStatements, PriceData
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


class FinancialDataLoader:
    """Load normalized data independently, allowing price/financials to fallback separately."""

    def __init__(self, provider_manager: ProviderManager | None = None, adapter=None):
        self.provider_manager = provider_manager
        self.adapter = adapter or YahooFinanceAdapter()

    def _load_yahoo(self, symbol: str):
        return self.adapter.price(symbol), self.adapter.financial_statements(symbol)

    def load(self, symbol: str) -> FinancialSnapshot:
        canonical = str(symbol).strip().upper()
        if not canonical:
            raise ValueError("Ticker vacío")

        if self.provider_manager is None:
            price, financials = self._load_yahoo(canonical)
            return FinancialSnapshot(price, financials, "yahoo", "yahoo", canonical, canonical)

        price_response = self.provider_manager.execute_with_fallback(canonical, "get_price")
        financial_response = self.provider_manager.execute_with_fallback(canonical, "get_financial_statements")
        if not price_response.success:
            raise RuntimeError(f"No fue posible obtener precio para {canonical}: {price_response.error}")
        if not financial_response.success:
            raise RuntimeError(f"No fue posible obtener estados financieros para {canonical}: {financial_response.error}")

        price = _ensure_type(price_response.data, PriceData, "precio")
        financials = _ensure_type(financial_response.data, FinancialStatements, "estados financieros")
        return FinancialSnapshot(
            price=price,
            financials=financials,
            price_provider=price_response.provider,
            financials_provider=financial_response.provider,
            price_provider_symbol=price_response.provider_symbol or canonical,
            financials_provider_symbol=financial_response.provider_symbol or canonical,
        )


def _ensure_type(value: Any, expected, label: str):
    if not isinstance(value, expected):
        raise TypeError(f"El provider devolvió un objeto no normalizado para {label}: {type(value).__name__}")
    return value
