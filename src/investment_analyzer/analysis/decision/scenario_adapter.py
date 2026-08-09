"""Normalize valuation scenarios from heterogeneous provider outputs.

Never invent Bear/Base/Bull values. Missing scenarios remain None.
Technical targets are deliberately excluded from Base/Fair Value extraction.
"""
from __future__ import annotations

from typing import Any


def _positive(value):
    try:
        value = float(value)
        return value if value > 0 else None
    except (TypeError, ValueError):
        return None


def _find(data: Any, names: tuple[str, ...]):
    wanted = {n.lower() for n in names}
    if isinstance(data, dict):
        for key, value in data.items():
            if str(key).lower() in wanted:
                found = _positive(value)
                if found is not None:
                    return found
        for value in data.values():
            found = _find(value, names)
            if found is not None:
                return found
    return None


def normalize_scenarios(valuation: Any) -> dict[str, float | None]:
    return {
        "bear": _find(valuation, ("bear", "bear_value", "bear_case", "bear_price", "downside_case")),
        "base": _find(valuation, (
            "fair_value_per_share",
            "fair_value",
            "intrinsic_value",
            "base",
            "base_value",
            "base_case",
        )),
        "bull": _find(valuation, ("bull", "bull_value", "bull_case", "bull_price", "upside_case")),
    }
