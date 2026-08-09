"""Source-checkout compatibility shim for the src-layout package."""
from __future__ import annotations

from pathlib import Path

# When running directly from the repository without an editable install,
# expose the real package located under src/investment_analyzer.
_real_package = Path(__file__).resolve().parent.parent / "src" / "investment_analyzer"
if _real_package.is_dir():
    __path__.append(str(_real_package))
