"""Human-readable rendering of the executable V12 trade plan."""
from __future__ import annotations


def _fmt(value, digits=2):
    if value is None:
        return "N/D"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def render_trade_plan(plan: dict | None, final_decision: dict | None = None) -> str:
    plan = plan or {}
    final_decision = final_decision or {}
    lines = ["", "PLAN OPERATIVO", "-" * 72]
    for key, label in (
        ("operation", "Operación plan"),
        ("entry", "Entry"),
        ("stop_loss", "Stop Loss"),
        ("target_1", "Target 1"),
        ("target_2", "Target 2"),
        ("bear_value", "Bear Case"),
        ("base_fair_value", "Fair Value"),
        ("bull_value", "Bull Case"),
        ("margin_of_safety_pct", "Margin of Safety %"),
        ("risk_reward", "R/R"),
        ("units", "Unidades"),
        ("position_value", "Inversión"),
        ("risk_budget", "Riesgo máximo"),
        ("actual_risk", "Riesgo real"),
    ):
        value = plan.get(key)
        digits = 1 if key == "margin_of_safety_pct" else 2
        lines.append(f"  {label:22s}: {_fmt(value, digits)}")

    final = final_decision.get("decision")
    if final:
        lines.append(f"  DECISIÓN FINAL        : {final}")
        lines.append(f"  Estado Quality Gate   : {_fmt(final_decision.get('status'), 0)}")

    reasons = plan.get("reasons") or final_decision.get("reasons") or []
    if reasons:
        lines.append("  Bloqueos:")
        lines.extend(f"    - {reason}" for reason in reasons)
    else:
        lines.append("  Quality Gate           : APROBADO")
    lines.append("-" * 72)
    return "\n".join(lines)
