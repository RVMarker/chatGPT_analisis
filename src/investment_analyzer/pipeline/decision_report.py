"""Human-readable CLI report for the V11 investment decision."""
from __future__ import annotations

from typing import Any


def _fmt(value: Any, digits: int = 1) -> str:
    if value is None:
        return "N/D"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def _get(obj: Any, *keys: str, default=None):
    for key in keys:
        if isinstance(obj, dict) and key in obj:
            return obj[key]
        if hasattr(obj, key):
            return getattr(obj, key)
    return default


def render_decision_report(context) -> str:
    decision = context.decision
    strategic = _get(decision, "strategic", "strategic_decision", default={})
    tactical = _get(decision, "tactical", "tactical_decision", default={})
    confidence = _get(decision, "confidence", default=None)
    metadata = getattr(context, "metadata", {}) or {}
    providers = metadata.get("data_providers", {})

    lines = [
        "=" * 72,
        "V11 — INFORME DE DECISIÓN DE INVERSIÓN",
        "=" * 72,
        f"Activo: {_get(context.asset, 'symbol', default='N/D')}",
        "",
        "DECISIÓN ESTRATÉGICA (años)",
        f"  Veredicto : {_get(strategic, 'verdict', 'decision', default='N/D')}",
        f"  Score     : {_fmt(_get(strategic, 'score', default=None))}/100",
        "",
        "DECISIÓN TÁCTICA (semanas)",
        f"  Veredicto : {_get(tactical, 'verdict', 'decision', default='N/D')}",
        f"  Score     : {_fmt(_get(tactical, 'score', default=None))}/100",
        "",
        "CONFIANZA",
        f"  {_fmt(confidence)}",
        "",
        "DATOS UTILIZADOS",
        f"  Precio       : {providers.get('price', 'N/D')} ({providers.get('price_symbol', 'N/D')})",
        f"  Financieros : {providers.get('financials', 'N/D')} ({providers.get('financials_symbol', 'N/D')})",
        "",
        "CONTEXTO — NO VOTA DIRECTAMENTE",
        f"  Comparables : {'disponible' if getattr(context, 'comparables', None) else 'N/D'}",
        f"  Macro       : {'disponible' if getattr(context, 'macro', None) else 'N/D'}",
        "=" * 72,
    ]
    return "\n".join(lines)


def print_decision_report(context) -> None:
    print(render_decision_report(context))
