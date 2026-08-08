"""Optional yfinance adapter.

Yahoo is the canonical symbol namespace. The adapter deliberately keeps the
third-party dependency optional so the core package and unit tests remain
usable without network access or yfinance installed.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from investment_analyzer.common.models import (
    BalanceSheet, CashFlow, FinancialStatements, IncomeStatement, PriceData, PriceHistory,
)


class YahooFinanceAdapter:
    provider_name = "yahoo"

    def __init__(self, yf_module: Any | None = None) -> None:
        if yf_module is None:
            try:
                import yfinance as yf  # type: ignore
            except ImportError as exc:
                raise RuntimeError("yfinance no está instalado. Instala la dependencia para usar Yahoo.") from exc
            yf_module = yf
        self.yf = yf_module

    def _ticker(self, symbol: str):
        return self.yf.Ticker(symbol.upper())

    @staticmethod
    def _value(mapping: Any, *keys: str, default=None):
        for key in keys:
            try:
                value = mapping.get(key)
            except AttributeError:
                value = None
            if value is not None:
                return value
        return default

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

    @staticmethod
    def _reconcile_share_count(
        shares: float | None,
        market_cap: float | None,
        current_price: float | None,
    ) -> tuple[float | None, float | None, str | None, float | None]:
        """Validate Yahoo's share count against market-cap/price.

        Some providers expose a share count with a unit/scale mismatch. We do
        not silently trust it when it conflicts materially with the provider's
        own market-cap and price. The implied count is used only when the
        discrepancy is clearly a scale problem (roughly 1,000x or 1,000,000x).
        """
        raw = None if shares is None else float(shares)
        if raw is not None and raw <= 0:
            raw = None
        implied = None
        if market_cap is not None and current_price is not None and float(current_price) > 0:
            mc = float(market_cap)
            px = float(current_price)
            if mc > 0:
                implied = mc / px

        if raw is None and implied is not None:
            return implied, None, "market_cap/current_price", None
        if raw is None:
            return None, None, None, None
        if implied is None:
            return raw, raw, "yahoo_fast_info", 1.0

        ratio = raw / implied
        abs_ratio = abs(ratio)
        for scale in (1_000_000.0, 1_000.0, 0.001, 0.000001):
            if abs(ratio / scale - 1.0) <= 0.05:
                normalized = raw / scale
                return normalized, raw, "yahoo_fast_info_reconciled", scale

        # A normal disagreement can occur because quote and market-cap fields
        # are not sampled at exactly the same instant. Keep the provider value
        # rather than manufacturing a new figure.
        return raw, raw, "yahoo_fast_info", 1.0

    def price_history(self, symbol: str, period: str = "2y", interval: str = "1d") -> PriceHistory:
        ticker = self._ticker(symbol)
        frame = ticker.history(period=period, interval=interval, auto_adjust=False)
        if frame is None or getattr(frame, "empty", True):
            raise ValueError(f"Yahoo no devolvió histórico para {symbol}")
        required = ("Open", "High", "Low", "Close", "Volume")
        missing = [column for column in required if column not in frame.columns]
        if missing:
            raise ValueError(f"Yahoo histórico incompleto para {symbol}: faltan {', '.join(missing)}")
        frame = frame.dropna(subset=["Close"]).copy()
        return PriceHistory(
            symbol=symbol.upper(), dates=list(frame.index),
            open=[float(x) for x in frame["Open"].fillna(frame["Close"]).tolist()],
            high=[float(x) for x in frame["High"].fillna(frame["Close"]).tolist()],
            low=[float(x) for x in frame["Low"].fillna(frame["Close"]).tolist()],
            close=[float(x) for x in frame["Close"].tolist()],
            volume=[float(x) for x in frame["Volume"].fillna(0).tolist()], interval=interval,
        )

    def price(self, symbol: str) -> PriceData:
        ticker = self._ticker(symbol)
        info = getattr(ticker, "fast_info", {}) or {}
        current = self._value(info, "last_price", "lastPrice")
        previous = self._value(info, "previous_close", "previousClose")
        if current is None:
            history = ticker.history(period="5d", auto_adjust=False)
            if history.empty:
                raise ValueError(f"Yahoo no devolvió precios para {symbol}")
            closes = history["Close"].dropna()
            current = float(closes.iloc[-1])
            previous = float(closes.iloc[-2]) if len(closes) > 1 else None
        market_cap = self._value(info, "market_cap", "marketCap")
        raw_shares = self._value(info, "shares")
        shares, shares_raw, shares_source, shares_scale = self._reconcile_share_count(
            raw_shares, market_cap, current,
        )
        return PriceData(
            symbol=symbol.upper(), current=float(current),
            previous_close=None if previous is None else float(previous),
            open=self._value(info, "open"), high=self._value(info, "day_high", "dayHigh"),
            low=self._value(info, "day_low", "dayLow"),
            volume=self._value(info, "three_month_average_volume", "threeMonthAverageVolume"),
            market_cap=market_cap, shares_outstanding=shares, beta=None,
            currency=self._value(info, "currency", default="USD") or "USD",
            timestamp=datetime.now(timezone.utc),
            shares_outstanding_raw=shares_raw,
            shares_outstanding_source=shares_source,
            shares_outstanding_scale=shares_scale,
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
        depreciation = self._latest_statement_value(
            cashflow,
            "Depreciation And Amortization",
            "Depreciation",
            "Depreciation Amortization Depletion",
        )
        property_gain = self._latest_statement_value(
            cashflow,
            "Gain Loss On Sale Of Assets",
            "Gain Loss On Sale Of Investments",
        )
        net_income = inc.net_income
        ffo_proxy = None
        if net_income is not None and depreciation is not None:
            # Conservative proxy: no gain-on-sale adjustment unless Yahoo supplies it.
            ffo_proxy = net_income + depreciation
            if property_gain is not None:
                ffo_proxy -= property_gain
        cf = CashFlow(
            operating_cash_flow=self._latest_statement_value(cashflow, "Operating Cash Flow", "Total Cash From Operating Activities"),
            capex=self._latest_statement_value(cashflow, "Capital Expenditure", "Capital Expenditure Reported"),
            free_cash_flow=self._latest_statement_value(cashflow, "Free Cash Flow"),
            dividends_paid=self._latest_statement_value(cashflow, "Cash Dividends Paid"),
            # yfinance's Ticker.cashflow endpoint is the annual cash-flow
            # statement. Mark that explicitly so payout cannot silently mix
            # an annual distribution with quarterly/monthly FFO.
            dividends_paid_period="annual" if cashflow is not None and not getattr(cashflow, "empty", True) else None,
            share_buybacks=self._latest_statement_value(cashflow, "Repurchase Of Capital Stock"),
            depreciation_amortization=depreciation,
            property_gain_loss=property_gain,
            ffo_proxy=ffo_proxy,
        )
        if cf.free_cash_flow is None and cf.operating_cash_flow is not None and cf.capex is not None:
            cf.free_cash_flow = cf.operating_cash_flow + cf.capex
        dates = getattr(balance, "columns", [])
        fiscal_date = str(dates[0]) if len(dates) else None
        return FinancialStatements(balance=bs, income=inc, cashflow=cf, fiscal_date=fiscal_date)
