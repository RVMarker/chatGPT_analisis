"""
AnalysisContext

Reemplaza el enorme diccionario que actualmente devuelve
analizar_activo().

Toda la V11 utilizará este objeto.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any


# ==============================================================
# CONTEXTO PRINCIPAL
# ==============================================================

@dataclass(slots=True)

class AnalysisContext:

    # ----------------------------------------------------------
    # Datos descargados
    # ----------------------------------------------------------

    asset: Any

    # AssetData

    # ----------------------------------------------------------
    # Técnico
    # ----------------------------------------------------------

    technical: dict = field(default_factory=dict)

    technical_result: dict = field(default_factory=dict)

    # ----------------------------------------------------------
    # Fundamental
    # ----------------------------------------------------------

    fundamentals: dict = field(default_factory=dict)

    # ----------------------------------------------------------
    # Valor Intrínseco
    # ----------------------------------------------------------

    valuation: dict = field(default_factory=dict)

    # ----------------------------------------------------------
    # DCF
    # ----------------------------------------------------------

    dcf: dict = field(default_factory=dict)

    # ----------------------------------------------------------
    # Riesgo
    # ----------------------------------------------------------

    risk: dict = field(default_factory=dict)

    # ----------------------------------------------------------
    # Comparables
    # ----------------------------------------------------------

    comparables: dict = field(default_factory=dict)

    # ----------------------------------------------------------
    # Sentimiento
    # ----------------------------------------------------------

    sentiment: dict = field(default_factory=dict)

    # ----------------------------------------------------------
    # Macro
    # ----------------------------------------------------------

    macro: dict = field(default_factory=dict)

    # ----------------------------------------------------------
    # ESG
    # ----------------------------------------------------------

    esg: dict = field(default_factory=dict)

    # ----------------------------------------------------------
    # Porter
    # ----------------------------------------------------------

    porter: dict = field(default_factory=dict)

    # ----------------------------------------------------------
    # Elliott
    # ----------------------------------------------------------

    elliott: dict = field(default_factory=dict)

    # ----------------------------------------------------------
    # Dow
    # ----------------------------------------------------------

    dow: dict = field(default_factory=dict)

    # ----------------------------------------------------------
    # Riesgo histórico
    # ----------------------------------------------------------

    performance: dict = field(default_factory=dict)

    # ----------------------------------------------------------

    pivot: dict = field(default_factory=dict)

    # ----------------------------------------------------------

    strategy: dict = field(default_factory=dict)

    # ----------------------------------------------------------

    signals: dict = field(default_factory=dict)

    # ----------------------------------------------------------

    projections: dict = field(default_factory=dict)

    # ----------------------------------------------------------

    agents: dict = field(default_factory=dict)

    # ----------------------------------------------------------

    profile: dict = field(default_factory=dict)

    # ----------------------------------------------------------

    seasonality: dict = field(default_factory=dict)

    # ----------------------------------------------------------

    backtest: dict = field(default_factory=dict)

    # ----------------------------------------------------------

    pe_history: dict = field(default_factory=dict)

    # ----------------------------------------------------------

    decision: Any = None

    # ----------------------------------------------------------

    generated_files: dict = field(default_factory=dict)