"""Make the src-layout package importable from a source checkout.

This keeps `python orchestrator.py` and `python -m investment_analyzer.cli`
working before an editable install, which is useful for Windows/VSCode CLI
validation and does not change installed-package behavior.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
