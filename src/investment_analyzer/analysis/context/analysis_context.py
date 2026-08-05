"""AnalysisContext shared by every V11 pipeline stage."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AnalysisContext:
    asset: Any
    technical: dict = field(default_factory=dict)
    technical_result: dict = field(default_factory=dict)
    fundamentals: dict = field(default_factory=dict)
    valuation: dict = field(default_factory=dict)
    dcf: dict = field(default_factory=dict)
    risk: dict = field(default_factory=dict)
    comparables: dict = field(default_factory=dict)
    sentiment: dict = field(default_factory=dict)
    macro: dict = field(default_factory=dict)
    esg: dict = field(default_factory=dict)
    porter: dict = field(default_factory=dict)
    elliott: dict = field(default_factory=dict)
    dow: dict = field(default_factory=dict)
    performance: dict = field(default_factory=dict)
    pivot: dict = field(default_factory=dict)
    strategy: dict = field(default_factory=dict)
    signals: dict = field(default_factory=dict)
    projections: dict = field(default_factory=dict)
    agents: dict = field(default_factory=dict)
    profile: dict = field(default_factory=dict)
    seasonality: dict = field(default_factory=dict)
    backtest: dict = field(default_factory=dict)
    pe_history: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    decision: Any = None
    generated_files: dict = field(default_factory=dict)
