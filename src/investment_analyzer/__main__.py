"""Allow ``python -m investment_analyzer`` to execute the V11 CLI."""
from __future__ import annotations

from investment_analyzer.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
