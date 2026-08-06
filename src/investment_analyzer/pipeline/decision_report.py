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


def _breakdown_lines(title: str, items: Any) -> list[str]:
    lines = [title]
    if not items:
        lines.append("  N/D")
        return lines
    for item in items:
        name = _get(item, "name", default="N/D")
        score = _get(item, "score", default=None)
        weight = _get(item, "weight", default=None)
        weighted = _get(item, "weighted", "weighted_contribution", default=None)
        contribution = _get(item, "contribution_pct", default=None)
        weight_pct = weight * 100 if isinstance(weight, (int, float)) else weight
        contribution_text = f" aporte%={_fmt(contribution, 1)}" if contribution is not None else ""
        lines.append(
            f"  {name:15s} score={_fmt(score, 2):>6} "
            f"peso={_fmt(weight_pct, 1)}% aporte={_fmt(weighted, 2):>6}{contribution_text}"
        )
    return lines


def render_decision_report(context) -> str:
    decision = context.decision
    strategic_verdict = _get(decision, "strategic_decision", "strategic_verdict", default="N/D")
    tactical_verdict = _get(decision, "tactical_decision", "tactical_verdict", default="N/D")
    strategic_score = _get(decision, "strategic_score", default=None)
    tactical_score = _get(decision, "tactical_score", default=None)
    confidence = _get(decision, "confidence", default=None)
    metadata = getattr(context, "metadata", {}) or {}
    providers = metadata.get("data_providers", {})
    strategic_breakdown = _get(decision, "strategic_breakdown", default=[])
    tactical_breakdown = _get(decision, "tactical_breakdown", default=[])
    contextual = _get(decision, "contextual", default={}) or {}
    strengths = _get(decision, "strengths", default=[]) or []
    red_flags = _get(decision, "red_flags", default=[]) or []

    lines = [
        "=" * 72,
        "V11 — INFORME DE DECISIÓN DE INVERSIÓN",
        "=" * 72,
        f"Activo: {_get(context.asset, 'symbol', default='N/D')}",
        "",
        "DECISIÓN ESTRATÉGICA (años)",
        f"  Veredicto : {strategic_verdict}",
        f"  Score     : {_fmt(strategic_score, 2)}/100",
        "",
        "DECISIÓN TÁCTICA (semanas)",
        f"  Veredicto : {tactical_verdict}",
        f"  Score     : {_fmt(tactical_score, 2)}/100",
        "",
        "CONFIANZA",
        f"  {_fmt(confidence, 1)}%",
        "",
    ]
    lines.extend(_breakdown_lines("DESGLOSE ESTRATÉGICO", strategic_breakdown))
    lines.append("")
    lines.extend(_breakdown_lines("DESGLOSE TÁCTICO", tactical_breakdown))
    lines.extend([
        "",
        "DATOS UTILIZADOS",
        f"  Precio        : {providers.get('price', 'N/D')} ({providers.get('price_symbol', 'N/D')})",
        f"  Financieros   : {providers.get('financials', 'N/D')} ({providers.get('financials_symbol', 'N/D')})",
        f"  Histórico     : {providers.get('history', 'N/D')} ({providers.get('history_symbol', 'N/D')})",
        f"  Observaciones : {providers.get('history_length', 'N/D')}",
        "",
        "CONTEXTO — NO VOTA DIRECTAMENTE",
    ])
    if contextual:
        for key, value in contextual.items():
            lines.append(f"  {key:15s} {_fmt(value, 2)}")
    else:
        lines.append("  N/D")

    if strengths:
        lines.extend(["", "FORTALEZAS"])
        lines.extend(f"  + {item}" for item in strengths)
    if red_flags:
        lines.extend(["", "RED FLAGS"])
        lines.extend(f"  - {item}" for item in red_flags)

    lines.append("=" * 72)
    return "\n".join(lines)


def print_decision_report(context) -> None:
    print(render_decision_report(context))
