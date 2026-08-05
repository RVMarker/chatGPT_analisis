"""Load normalized market/financial data for the financial pipeline stage."""
from __future__ import annotations

from dataclasses import dataclass

from investment_analyzer.common.models import FinancialStatements, PriceData
from investment_analyzer.providers.yahoo_adapter import YahooFinanceAdapter


@dataclass(slots=True)
class FinancialSnapshot:
    price: PriceData
    financials: FinancialStatements


class FinancialDataLoader:
    """Yahoo-backed loader; the input symbol remains the canonical Yahoo symbol."""

    def __init__(self, adapter=None):
        self.adapter = adapter or YahooFinanceAdapter()

    def load(self, symbol: str) -> FinancialSnapshot:
        canonical = symbol.strip().upper()
        if not canonical:
            raise ValueError("Ticker vacío")
        return FinancialSnapshot(
            price=self.adapter.price(canonical),
            financials=self.adapter.financial_statements(canonical),
        )
