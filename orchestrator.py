"""Interactive V12 CLI wrapper.

All scoring, scenario handling, trade planning and final decision logic lives
in the production application path. This file only collects interactive CLI
parameters so there is one source of truth for investment decisions.

The source checkout is supported as well as an editable installation: when
called directly from the repository root, ``src`` is added to ``sys.path`` so
users do not get a misleading ``investment_analyzer`` import error before
installation.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from investment_analyzer.app import run_application


def run() -> int:
    ticker = input("Activo a analizar: ").strip()
    if not ticker:
        raise SystemExit("Debe indicar un activo.")
    capital = float(input("Capital disponible [5000]: ") or "5000")
    risk_pct = float(input("Riesgo máximo por operación % [2]: ") or "2")
    max_position_pct = float(input("Máximo por posición % [25]: ") or "25")
    return run_application(
        ticker,
        capital=capital,
        risk_pct=risk_pct / 100.0,
        max_position_pct=max_position_pct / 100.0,
    )


if __name__ == "__main__":
    raise SystemExit(run())
