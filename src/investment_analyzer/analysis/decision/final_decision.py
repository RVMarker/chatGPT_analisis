"""Final investment decision gate for V12.

The strategic thesis controls direction. The executable trade plan controls
whether a new long entry is actually actionable. Contextual macro/comparables
never vote here.
"""
from __future__ import annotations


def finalize_decision(strategic_decision: str | None, trade_plan: dict | None) -> dict:
    strategic = str(strategic_decision or "N/D").upper()
    plan = trade_plan or {}
    operation = str(plan.get("operation") or "ESPERAR").upper()
    reasons = list(plan.get("reasons") or [])

    if strategic == "VENDER":
        final = "VENDER"
        status = "THESIS_NEGATIVE"
    elif strategic == "REDUCIR":
        final = "REDUCIR"
        status = "THESIS_NEGATIVE"
    elif strategic == "MANTENER":
        final = "MANTENER"
        status = "NO_NEW_ENTRY"
    elif strategic in {"COMPRAR", "ACUMULAR"}:
        if operation == "COMPRAR":
            final = strategic
            status = "TRADE_PLAN_APPROVED"
        else:
            final = "ESPERAR"
            status = "TRADE_PLAN_BLOCKED"
    else:
        final = "ESPERAR"
        status = "INSUFFICIENT_EVIDENCE"

    return {
        "decision": final,
        "status": status,
        "strategic_decision": strategic,
        "trade_plan_operation": operation,
        "reasons": reasons,
    }
