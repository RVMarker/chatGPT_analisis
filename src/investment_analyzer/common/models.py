"""
models.py
Investment Analyzer v11

Modelos comunes utilizados por todos los módulos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class PriceData:
    symbol: str
    current: float
    previous_close: float | None = None
    open: float | None = None
    high: float | None = None
    low: float | None = None
    volume: float | None = None
    market_cap: float | None = None
    shares_outstanding: float | None = None
    beta: float | None = None
    currency: str = "USD"
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class PriceHistory:
    symbol: str
    dates: list[Any] = field(default_factory=list)
    open: list[float] = field(default_factory=list)
    high: list[float] = field(default_factory=list)
    low: list[float] = field(default_factory=list)
    close: list[float] = field(default_factory=list)
    volume: list[float] = field(default_factory=list)
    interval: str = "1d"

    def __len__(self) -> int:
        return len(self.close)


@dataclass(slots=True)
class BalanceSheet:
    total_assets: float | None = None
    current_assets: float | None = None
    cash: float | None = None
    inventory: float | None = None
    receivables: float | None = None
    total_liabilities: float | None = None
    current_liabilities: float | None = None
    long_term_debt: float | None = None
    shareholders_equity: float | None = None
    retained_earnings: float | None = None
    working_capital: float | None = None
    property_value: float | None = None


@dataclass(slots=True)
class IncomeStatement:
    revenue: float | None = None
    gross_profit: float | None = None
    operating_income: float | None = None
    ebit: float | None = None
    ebitda: float | None = None
    pretax_income: float | None = None
    net_income: float | None = None
    eps: float | None = None
    interest_expense: float | None = None


@dataclass(slots=True)
class CashFlow:
    operating_cash_flow: float | None = None
    capex: float | None = None
    free_cash_flow: float | None = None
    dividends_paid: float | None = None
    # Period of the total cash-flow value. Payout/FFO may only compare values
    # on the same period basis; the REIT engine requires an explicit period.
    dividends_paid_period: str | None = None
    share_buybacks: float | None = None
    depreciation_amortization: float | None = None
    property_gain_loss: float | None = None
    ffo_proxy: float | None = None
    ffo_official: float | None = None
    affo_official: float | None = None
    recurring_capex: float | None = None


@dataclass(slots=True)
class FinancialStatements:
    balance: BalanceSheet
    income: IncomeStatement
    cashflow: CashFlow
    fiscal_date: str | None = None


@dataclass(slots=True)
class TechnicalIndicators:
    rsi: float | None = None
    macd: float | None = None
    signal: float | None = None
    atr: float | None = None
    adx: float | None = None
    sma20: float | None = None
    sma50: float | None = None
    sma200: float | None = None
    ema20: float | None = None
    bollinger_position: float | None = None


@dataclass(slots=True)
class FundamentalRatios:
    roe: float | None = None
    roa: float | None = None
    roic: float | None = None
    current_ratio: float | None = None
    quick_ratio: float | None = None
    debt_equity: float | None = None
    debt_ebitda: float | None = None
    interest_coverage: float | None = None
    gross_margin: float | None = None
    operating_margin: float | None = None
    net_margin: float | None = None


@dataclass(slots=True)
class ValuationData:
    market_price: float
    intrinsic_value: float
    upside: float
    margin_of_safety: float
    fair_value_low: float | None = None
    fair_value_high: float | None = None
    pe: float | None = None
    ev_ebitda: float | None = None
    peg: float | None = None


@dataclass(slots=True)
class RiskMetrics:
    altman_z: float | None = None
    piotroski: float | None = None
    beta: float | None = None
    volatility: float | None = None
    sharpe: float | None = None
    sortino: float | None = None
    max_drawdown: float | None = None


@dataclass(slots=True)
class MacroData:
    risk_free_rate: float | None = None
    inflation: float | None = None
    fed_rate: float | None = None
    unemployment: float | None = None
    recession_probability: float | None = None


@dataclass(slots=True)
class NewsItem:
    title: str
    date: str
    sentiment: float
    source: str
    url: str


@dataclass(slots=True)
class ProviderResult:
    provider: str
    timestamp: datetime
    success: bool
    latency_ms: float
    payload: Any


@dataclass(slots=True)
class AnalysisResult:
    module: str
    score: float
    explanation: str
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
