"""Optional yfinance adapter.

Yahoo is the canonical symbol namespace. The adapter deliberately keeps the
third-party dependency optional so the core package and unit tests remain
usable without network access or yfinance installed.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from investment_analyzer.common.models import (
    BalanceSheet,
    CashFlow,
    FinancialStatements,
    IncomeStatement,
    PriceData,
)


class YahooFinanceAdapter:
    provider_name = "yahoo"

    def __init__(self, yf_module: Any | None = None) -> None:
        if yf_module is None:
            try:
                import yfinance as yf  # type: ignore
            except ImportError as exc:
                raise RuntimeError(
                    "yfinance no está instalado. Instala la dependencia para usar Yahoo."
                ) from exc
            yf_module = yf
        self.yf = yf_module

    def _ticker(self, symbol: str):
        # El símbolo recibido aquí es SIEMPRE el canónico de Yahoo.
        return self.yf.Ticker(symbol.upper())

    @staticmethod
    def _value(mapping: Any, *keys: str):
        for key in keys:
            try:
                value = mapping.get(key)
            except AttributeError:
                value = None
            if value is not None:
                return value
        return None

    @classmethod
    def _latest_statement_value(cls, frame: Any, *keys: str):
        if frame is None or getattr(frame, "empty", True):
            return None
        for key in keys:
            try:
                if key in frame.index:
                    row = frame.loc[key]
                    for value in row.tolist():
                        if value is not None:
                            try:
                                if value == value:
                                    return float(value)
                            except (TypeError, ValueError):
                                continue
            except (KeyError, TypeError, AttributeError):
                continue
        return None

    def price(self, symbol: str) -> PriceData:
        ticker = self._ticker(symbol)
        info = getattr(ticker, "fast_info", {}) or {}
        current = self._value(info, "last_price", "lastPrice")
        if current is None:
            history = ticker.history(period="5d", auto_adjust=False)
            if history.empty:
                raise ValueError(f"Yahoo no devolvió precios para {symbol}")
            current = float(history["Close"].dropna().iloc[-1])
            previous = float(history["Close"].dropna().iloc[-2]) if len(history) > 1 else None
        else:
            previous = self._value(info, "previous_close", "previousClose")
        return PriceData(
            symbol=symbol.upper(),
            current=float(current),
            previous_close=None if previous is None else float(previous),
            open=self._value(info, "open"),
            high=self._value(info, "day_high", "dayHigh"),
            low=self._value(info, "day_low", "dayLow"),
            volume=self._value(info, "three_month_average_volume", "threeMonthAverageVolume"),
            market_cap=self._value(info, "market_cap", "marketCap"),
            shares_outstanding=self._value(info, "shares"),
            beta=None,
            currency=self._value(info, "currency", default="USD") or "USD",
            timestamp=datetime.now(timezone.utc),
        )

    def financial_statements(self, symbol: str) -> FinancialStatements:
        ticker = self._ticker(symbol)
        balance = getattr(ticker, "balance_sheet", None)
        income = getattr(ticker, "income_stmt", None)
        cashflow = getattr(ticker, "cashflow", None)

        bs = BalanceSheet(
            total_assets=self._latest_statement_value(balance, "Total Assets"),
            current_assets=self._latest_statement_value(balance, "Current Assets"),
            cash=self._latest_statement_value(balance, "Cash Cash Equivalents And Short Term Investments", "Cash And Cash Equivalents"),
            inventory=self._latest_statement_value(balance, "Inventory"),
            receivables=self._latest_statement_value(balance, "Receivables", "Accounts Receivable"),
            total_liabilities=self._latest_statement_value(balance, "Total Liabilities Net Minority Interest", "Total Liabilities"),
            current_liabilities=self._latest_statement_value(balance, "Current Liabilities"),
            long_term_debt=self._latest_statement_value(balance, "Long Term Debt", "Long Term Debt And Capital Lease Obligation"),
            shareholders_equity=self._latest_statement_value(balance, "Stockholders Equity", "Common Stock Equity"),
            retained_earnings=self._latest_statement_value(balance, "Retained Earnings"),
        )
        if bs.current_assets is not None and bs.current_liabilities is not None:
            bs.working_capital = bs.current_assets - bs.current_liabilities

        inc = IncomeStatement(
            revenue=self._latest_statement_value(income, "Total Revenue", "Operating Revenue"),
            gross_profit=self._latest_statement_value(income, "Gross Profit"),
            operating_income=self._latest_statement_value(income, "Operating Income"),
            ebit=self._latest_statement_value(income, "EBIT", "Operating Income"),
            ebitda=self._latest_statement_value(income, "EBITDA", "Normalized EBITDA"),
            pretax_income=self._latest_statement_value(income, "Pretax Income"),
            net_income=self._latest_statement_value(income, "Net Income", "Net Income Common Stockholders"),
            eps=self._latest_statement_value(income, "Diluted EPS", "Basic EPS"),
            interest_expense=self._latest_statement_value(income, "Interest Expense Non Operating", "Interest Expense"),
        )
        cf = CashFlow(
            operating_cash_flow=self._latest_statement_value(cashflow, "Operating Cash Flow", "Total Cash From Operating Activities"),
            capex=self._latest_statement_value(cashflow, "Capital Expenditure", "Capital Expenditure Reported"),
            free_cash_flow=self._latest_statement_value(cashflow, "Free Cash Flow"),
            dividends_paid=self._latest_statement_value(cashflow, "Cash Dividends Paid"),
            share_buybacks=self._latest_statement_value(cashflow, "Repurchase Of Capital Stock"),
        )
        if cf.free_cash_flow is None and cf.operating_cash_flow is not None and cf.capex is not None:
            cf.free_cash_flow = cf.operating_cash_flow + cf.capex

        dates = getattr(balance, "columns", [])
        fiscal_date = str(dates[0]) if len(dates) else None
        return FinancialStatements(balance=bs, income=inc, cashflow=cf, fiscal_date=fiscal_date)
