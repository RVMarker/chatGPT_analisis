"""V12.60 CLI renderer: existing decision report + adaptive asset report."""
from __future__ import annotations
from investment_analyzer.report.multi_asset_report import MultiAssetReport


def render_complete_report(context)->str:
    return MultiAssetReport().render(context)
