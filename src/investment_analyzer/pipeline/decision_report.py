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
        return lines + ["  N/D"]
    for item in items:
        name = _get(item, "name", default="N/D")
        score = _get(item, "score", default=None)
        weight = _get(item, "weight", default=None)
        weighted = _get(item, "weighted", "weighted_contribution", default=None)
        contribution = _get(item, "contribution_pct", default=None)
        available = _get(item, "available", default=True)
        weight_pct = weight * 100 if isinstance(weight, (int, float)) else weight
        status = "[N/D]" if available is False else ""
        lines.append(f"  {name:15s} score={_fmt(score, 2):>6} peso={_fmt(weight_pct, 1)}% aporte={_fmt(weighted, 2):>6} aporte%={_fmt(contribution, 1):>5} {status}")
    return lines


def _qualified_verdict(verdict: str | None, sufficient: bool | None) -> str:
    if verdict is None:
        return "N/D"
    if sufficient is False and verdict != "N/D":
        return f"{verdict} — EVIDENCIA INSUFICIENTE"
    return verdict


def _macro_lines(macro: dict[str, Any]) -> list[str]:
    lines = ["MACRO — CONTEXTO (NO VOTA DIRECTAMENTE)"]
    if not isinstance(macro, dict):
        return lines + ["  N/D"]

    diagnostics = macro.get("diagnostics") or {}
    if not macro.get("available"):
        fred_status = "CONFIGURADA" if diagnostics.get("fred_configured") else "NO CONFIGURADA"
        banxico_status = "CONFIGURADA" if diagnostics.get("banxico_configured") else "NO CONFIGURADA"
        lines.extend([
            "  Estado             : SIN DATOS MACRO",
            f"  FRED API           : {fred_status}",
            f"  Banxico API        : {banxico_status}" if diagnostics.get("banxico_configured") is not None else "  Banxico API        : N/A",
            f"  Observaciones EUA  : {diagnostics.get('fred_observations', 0)}",
            f"  Observaciones MX   : {diagnostics.get('mexico_observations', 0)}",
        ])
        errors = diagnostics.get("errors") or []
        if errors:
            lines.append("  Errores             : " + "; ".join(errors))
        else:
            lines.append("  Diagnóstico         : configura las credenciales en .env y vuelve a ejecutar")
        lines.append("  Macro es contextual y no vota directamente en BUY/SELL/HOLD.")
        return lines

    lines.extend([
        f"  Proveedores       : {_fmt(macro.get('provider'), 0)}",
        f"  Margen requerido  : {_fmt(macro.get('required_margin'), 1)}%",
        f"  EUA régimen       : {_fmt(macro.get('us_regime'), 0)}",
        f"  EUA Fed funds     : {_fmt((macro.get('us') or {}).get('policy_rate'), 2)}%",
        f"  EUA inflación YoY : {_fmt((macro.get('us') or {}).get('inflation_yoy'), 2)}%",
        f"  EUA desempleo     : {_fmt((macro.get('us') or {}).get('unemployment'), 2)}%",
        f"  EUA PIB real YoY  : {_fmt((macro.get('us') or {}).get('real_gdp_yoy'), 2)}%",
        f"  EUA Treasury 10Y  : {_fmt((macro.get('us') or {}).get('treasury_10y'), 2)}%",
    ])
    mx = macro.get("mexico")
    if mx is not None:
        lines.extend([
            "  MÉXICO régimen    : " + _fmt(macro.get("mexico_regime"), 0),
            f"  MÉXICO Banxico    : {_fmt(mx.get('policy_rate'), 2)}%",
            f"  MÉXICO inflación   : {_fmt(mx.get('inflation_yoy'), 2)}%",
            f"  MÉXICO USD/MXN    : {_fmt(mx.get('usd_mxn'), 4)}",
            f"  MÉXICO Bono 10Y   : {_fmt(mx.get('treasury_10y'), 2)}%",
        ])
        cross = macro.get("cross_country") or {}
        lines.extend([
            f"  DIF. Banxico-Fed  : {_fmt(cross.get('policy_rate_spread_mx_us'), 2)} pp",
            f"  DIF. Bono 10Y     : {_fmt(cross.get('treasury_10y_spread_mx_us'), 2)} pp",
            f"  Tasa real MX ex-post: {_fmt(cross.get('mexico_real_rate_ex_post'), 2)}%",
        ])
    else:
        lines.append("  México             : No aplica; activo no identificado como .MX")
    errors = diagnostics.get("errors") or []
    if errors:
        lines.append("  Errores parciales  : " + "; ".join(errors))
    lines.append("  Lectura            : " + _fmt(macro.get("explanation"), 0))
    return lines


def render_decision_report(context) -> str:
    decision = context.decision
    strategic_verdict = _get(decision, "strategic_decision", "strategic_verdict", default=None)
    tactical_verdict = _get(decision, "tactical_decision", "tactical_verdict", default=None)
    strategic_score = _get(decision, "strategic_score", default=None)
    tactical_score = _get(decision, "tactical_score", default=None)
    if strategic_verdict is None:
        strategic = _get(decision, "strategic", default={}) or {}
        strategic_verdict = _get(strategic, "verdict", "decision", default="N/D")
        strategic_score = _get(strategic, "score", default=strategic_score)
    if tactical_verdict is None:
        tactical = _get(decision, "tactical", default={}) or {}
        tactical_verdict = _get(tactical, "verdict", "decision", default="N/D")
        tactical_score = _get(tactical, "score", default=tactical_score)

    strategic_sufficient = _get(decision, "strategic_sufficient", default=None)
    tactical_sufficient = _get(decision, "tactical_sufficient", default=None)
    strategic_coverage = _get(decision, "strategic_coverage", default=None)
    tactical_coverage = _get(decision, "tactical_coverage", default=None)
    confidence = _get(decision, "confidence", default=None)
    coverage = _get(decision, "data_coverage", default=None)
    base_confidence = _get(decision, "base_confidence", default=None)
    metadata = getattr(context, "metadata", {}) or {}
    providers = metadata.get("data_providers", {})
    strategic_breakdown = _get(decision, "strategic_breakdown", default=[])
    tactical_breakdown = _get(decision, "tactical_breakdown", default=[])
    contextual = _get(decision, "contextual", default={}) or {}
    strengths = _get(decision, "strengths", default=[]) or []
    red_flags = _get(decision, "red_flags", default=[]) or []
    valuation = getattr(context, "valuation", {}) or {}
    risk = getattr(context, "risk", {}) or {}
    comparables = getattr(context, "comparables", {}) or {}
    macro = getattr(context, "macro", {}) or {}
    financial_meta = metadata.get("financial_integration", {}) or {}

    valuation_model = valuation.get("model") or valuation.get("valuation_model") or "N/D"
    is_reit_valuation = valuation_model == "FFO_CAPITALIZATION"
    fair_value_label = "FFO fair value/share" if is_reit_valuation else "Fair value/share"
    margin_label = "FFO margin of safety" if is_reit_valuation else "Margin of safety"

    lines = ["=" * 72, "V11 — INFORME DE DECISIÓN DE INVERSIÓN", "=" * 72,
             f"Activo: {_get(context.asset, 'symbol', default='N/D')}", "",
             "DECISIÓN ESTRATÉGICA (años)",
             f"  Veredicto : {_qualified_verdict(strategic_verdict, strategic_sufficient)}",
             f"  Score     : {_fmt(strategic_score, 1)}/100",
             f"  Cobertura : {_fmt(strategic_coverage, 1)}%", "",
             "DECISIÓN TÁCTICA (semanas)",
             f"  Veredicto : {_qualified_verdict(tactical_verdict, tactical_sufficient)}",
             f"  Score     : {_fmt(tactical_score, 1)}/100",
             f"  Cobertura : {_fmt(tactical_coverage, 1)}%", "",
             "CALIDAD / CONFIANZA",
             f"  Calidad de datos base : {_fmt(base_confidence, 1)}%",
             f"  Cobertura decisoria   : {_fmt(coverage, 1)}%",
             f"  Confianza de decisión : {_fmt(confidence, 1)}%", ""]
    lines.extend(_breakdown_lines("DESGLOSE ESTRATÉGICO", strategic_breakdown)); lines.append("")
    lines.extend(_breakdown_lines("DESGLOSE TÁCTICO", tactical_breakdown))
    lines.extend(["", "COBERTURA FINANCIERA",
        f"  Fundamental : {'OK' if financial_meta.get('fundamental_available') else 'N/D'}",
        f"  Valuation   : {'OK' if financial_meta.get('valuation_available') else 'N/D'}",
        f"  Risk        : {'OK' if financial_meta.get('risk_available') else 'N/D'}",
        f"  Modelo valoración : {valuation_model}"])
    if is_reit_valuation:
        lines.append(f"  FFO/share           : {_fmt(valuation.get('ffo_per_share'), 4)}")
        lines.append(f"  Calidad FFO         : {_fmt(valuation.get('source_quality'), 0)}")
        lines.append(f"  Calidad valoración : {_fmt(valuation.get('valuation_quality'), 0)}")
    lines.extend([f"  {fair_value_label:<22}: {_fmt(valuation.get('fair_value_per_share'), 2)}",
        f"  {margin_label:<22}: {_fmt(valuation.get('margin_of_safety'), 1)}%" if valuation.get('margin_of_safety') is not None else f"  {margin_label:<22}: N/D",
        f"  Risk Altman Z        : {_fmt(risk.get('altman_score'), 2)}",
        f"  Risk D/E             : {_fmt(risk.get('debt_to_equity'), 2)}",
        f"  Risk market leverage : {_fmt(risk.get('market_leverage'), 2)}",
        f"  Risk current ratio   : {_fmt(risk.get('current_ratio'), 2)}", "",
        "DATOS UTILIZADOS",
        f"  Precio        : {providers.get('price', 'N/D')} ({providers.get('price_symbol', 'N/D')})",
        f"  Financieros   : {providers.get('financials', 'N/D')} ({providers.get('financials_symbol', 'N/D')})",
        f"  Histórico     : {providers.get('history', 'N/D')} ({providers.get('history_symbol', 'N/D')})",
        f"  Observaciones : {providers.get('history_length', 'N/D')}", "",
        "SENTIMENT — TRAZABILIDAD",
        f"  Proveedor     : {metadata.get('sentiment_provider') or 'N/D'} ({metadata.get('sentiment_provider_symbol') or 'N/D'})",
        f"  Noticias raw  : {metadata.get('sentiment_raw_count', 0)}",
        f"  Normalizadas  : {metadata.get('sentiment_normalized_count', 0)}",
        f"  Evidencias    : {len(metadata.get('sentiment_evidence', []) or [])}", "",
        "CONTEXTO — NO VOTA DIRECTAMENTE"])
    if contextual:
        for key, value in contextual.items(): lines.append(f"  {key:15s} {_fmt(value, 2)}")
    else: lines.append("  N/D")
    lines.extend(["", "COMPARABLES — CONTEXTO",
        f"  P/E activo       : {_fmt(comparables.get('pe'), 2)}",
        f"  P/E mediana peers: {_fmt(comparables.get('peer_pe_median'), 2)}",
        f"  P/E prima/descto : {_fmt(comparables.get('pe_premium_discount') * 100 if comparables.get('pe_premium_discount') is not None else None, 1)}%",
        f"  EV/EBITDA activo : {_fmt(comparables.get('ev_ebitda'), 2)}",
        f"  EV/EBITDA peers  : {_fmt(comparables.get('peer_ev_ebitda_median'), 2)}",
        f"  EV/EBITDA prima  : {_fmt(comparables.get('ev_ebitda_premium_discount') * 100 if comparables.get('ev_ebitda_premium_discount') is not None else None, 1)}%",
        f"  Lectura          : {comparables.get('context', 'N/D')}", ""])
    lines.extend(_macro_lines(macro))
    if strengths: lines.extend(["", "FORTALEZAS", *[f"  + {item}" for item in strengths]])
    if red_flags: lines.extend(["", "RED FLAGS", *[f"  - {item}" for item in red_flags]])
    lines.append("=" * 72)
    return "\n".join(lines)


def print_decision_report(context) -> None:
    print(render_decision_report(context))
