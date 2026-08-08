"""V11.7 actionable decision layer for the CLI report.

Keeps the existing V11 report intact and appends an auditable executive layer.
No new scoring is performed here: this module only explains DecisionResult.
"""
from __future__ import annotations
from typing import Any


def _get(obj: Any, key: str, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _pct(value):
    return "N/D" if value is None else f"{float(value):.1f}%"


def _score(value):
    return "N/D" if value is None else f"{float(value):.1f}/100"


def _action(verdict: str | None, score: float | None, confidence: float | None, robustness: str) -> tuple[str, str]:
    if not verdict or verdict == "N/D":
        return "SIN ACCIÓN", "No existe un veredicto suficiente para recomendar una acción."
    confidence = float(confidence or 0)
    score = float(score or 0)
    if verdict == "VENDER":
        if robustness == "ALTA" and confidence >= 75:
            return "REDUCIR EXPOSICIÓN", "La tesis negativa es suficientemente robusta para reducir exposición."
        return "NO AUMENTAR / REVISAR TESIS", "El veredicto es negativo, pero la evidencia no justifica una acción agresiva por sí sola."
    if verdict == "COMPRAR":
        if robustness == "ALTA" and confidence >= 75:
            return "INICIAR / AUMENTAR POSICIÓN", "La tesis positiva presenta respaldo y calidad de datos suficientes."
        return "ENTRADA GRADUAL", "La tesis es positiva, pero conviene limitar el tamaño inicial mientras aumenta la evidencia."
    if verdict == "ACUMULAR":
        return "ACUMULAR GRADUALMENTE", "La señal es favorable, aunque no alcanza la convicción de una compra plena."
    if verdict == "REDUCIR":
        return "REDUCIR GRADUALMENTE", "Existe presión negativa, pero menor que la requerida para un VENDER robusto."
    return "MANTENER / ESPERAR", "La evidencia no exige modificar la posición actualmente."


def _robustness(decision, horizon: str) -> str:
    coverage = _get(decision, f"{horizon}_coverage", 0) or 0
    sufficient = _get(decision, f"{horizon}_sufficient", False)
    score = _get(decision, f"{horizon}_score", None)
    if not sufficient or coverage < 75 or score is None:
        return "BAJA"
    # Robust means the score is not sitting immediately on a decision boundary.
    boundaries = (35, 50, 70, 80)
    distance = min(abs(float(score) - b) for b in boundaries)
    if coverage >= 100 and distance >= 8:
        return "ALTA"
    return "MEDIA"


def render_actionable_layer(context) -> str:
    decision = getattr(context, "decision", None)
    if decision is None:
        return "\nDECISIÓN ACCIONABLE\n  N/D — no existe DecisionResult.\n"

    confidence = _get(decision, "confidence", None)
    strategic_score = _get(decision, "strategic_score", None)
    tactical_score = _get(decision, "tactical_score", None)
    strategic_verdict = _get(decision, "strategic_decision", "N/D")
    tactical_verdict = _get(decision, "tactical_decision", "N/D")
    strategic_robustness = _robustness(decision, "strategic")
    tactical_robustness = _robustness(decision, "tactical")
    strategic_action, strategic_reason = _action(strategic_verdict, strategic_score, confidence, strategic_robustness)
    tactical_action, tactical_reason = _action(tactical_verdict, tactical_score, confidence, tactical_robustness)

    decisive = list(_get(decision, "decisive_factors", []) or [])
    contextual = list(_get(decision, "contextual_factors", []) or [])
    missing = list(_get(decision, "missing_factors", []) or [])
    red_flags = list(_get(decision, "red_flags", []) or [])
    strengths = list(_get(decision, "strengths", []) or [])

    lines = [
        "",
        "=" * 72,
        "DECISIÓN ACCIONABLE — V11.7",
        "=" * 72,
        "ESTRATÉGICO",
        f"  Veredicto   : {strategic_verdict}",
        f"  Severidad   : {'ALTA' if strategic_score is not None and strategic_score < 35 else 'MODERADA' if strategic_score is not None and strategic_score < 50 else 'BAJA'}",
        f"  Robustez    : {strategic_robustness}",
        f"  Acción      : {strategic_action}",
        f"  Fundamento  : {strategic_reason}",
        "",
        "TÁCTICO",
        f"  Veredicto   : {tactical_verdict}",
        f"  Robustez    : {tactical_robustness}",
        f"  Acción      : {tactical_action}",
        f"  Fundamento  : {tactical_reason}",
        "",
        "FACTORES DECISIVOS — SÍ VOTAN",
    ]
    lines.extend(f"  • {item}" for item in decisive) if decisive else lines.append("  • N/D")
    lines.extend(["", "FACTORES CONTEXTUALES — NO VOTAN"])
    lines.extend(f"  • {item}" for item in contextual) if contextual else lines.append("  • N/D")
    lines.extend(["", "DATOS / FACTORES FALTANTES — REDUCEN CONFIANZA"])
    lines.extend(f"  • {item}" for item in missing) if missing else lines.append("  • Ninguno identificado por DecisionEngine")
    if strengths:
        lines.extend(["", "FORTALEZAS"])
        lines.extend(f"  • {item}" for item in strengths)
    if red_flags:
        lines.extend(["", "ALERTAS"])
        lines.extend(f"  • {item}" for item in red_flags)

    valuation = getattr(context, "valuation", {}) or {}
    sensitivity = valuation.get("sensitivity") if isinstance(valuation, dict) else None
    if sensitivity:
        base = sensitivity.get("base_case") or {}
        lines.extend([
            "",
            "ROBUSTEZ DE VALORACIÓN — SENSIBILIDAD",
            f"  Caso base : yield={float(base.get('yield', 0))*100:.1f}% | growth={float(base.get('growth', 0))*100:.1f}% | FV={base.get('fair_value', 'N/D')}",
            f"  Rango FV  : {_fmt_money(sensitivity.get('min_fair_value'))} a {_fmt_money(sensitivity.get('max_fair_value'))}",
        ])
        classifications = sensitivity.get("classifications") or {}
        counts = {"ATRACTIVE": 0, "NEUTRAL": 0, "DESFAVORABLE": 0, "N/D": 0}
        for row in classifications.values():
            for label in row.values(): counts[label] = counts.get(label, 0) + 1
        lines.append("  Escenarios: " + ", ".join(f"{k}={v}" for k, v in counts.items() if v))

    lines.extend([
        "",
        "INTERPRETACIÓN",
        "  El veredicto es una señal de decisión, no una orden automática de mercado.",
        "  Macro y comparables permanecen fuera del voto; se usan para contextualizar la tesis.",
        "  La acción sugerida debe considerar tamaño de posición, horizonte y tolerancia al riesgo.",
    ])
    return "\n".join(lines) + "\n"


def _fmt_money(value):
    return "N/D" if value is None else f"{float(value):.2f}"
