"""Command-line entry point for the V12 investment analyzer."""
from __future__ import annotations

import argparse

from investment_analyzer.app import attach_trade_plan, build_application
from investment_analyzer.pipeline.decision_report import render_decision_report
from investment_analyzer.pipeline.pipeline import AnalysisPipeline
from investment_analyzer.pipeline.trade_plan_report import render_trade_plan

# Backwards-compatible name retained for integrations that monkeypatch the
# renderer at the CLI boundary.
format_decision_report = render_decision_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="V12 Investment Analyzer")
    parser.add_argument("ticker", help="Ticker canónico, por ejemplo FMTY14.MX")
    parser.add_argument("--capital", type=float, default=5000.0, help="Capital disponible; default 5000")
    parser.add_argument("--risk-pct", type=float, default=2.0, help="Riesgo máximo por operación en porcentaje; default 2")
    parser.add_argument("--max-position-pct", type=float, default=25.0, help="Máximo de capital por posición en porcentaje; default 25")
    return parser


def run_cli(
    ticker: str,
    pipeline: AnalysisPipeline,
    capital: float = 5000.0,
    risk_pct: float = 2.0,
    max_position_pct: float = 25.0,
) -> int:
    if capital <= 0:
        raise ValueError("capital debe ser mayor que 0")
    if not 0 < risk_pct <= 100:
        raise ValueError("risk_pct debe estar entre 0 y 100")
    if not 0 < max_position_pct <= 100:
        raise ValueError("max_position_pct debe estar entre 0 y 100")

    context = pipeline.run(ticker)
    if hasattr(context, "price") and hasattr(context, "technical") and hasattr(context, "valuation"):
        attach_trade_plan(
            context,
            capital=capital,
            risk_pct=risk_pct / 100.0,
            max_position_pct=max_position_pct / 100.0,
        )
    print(format_decision_report(context))
    if hasattr(context, "trade_plan"):
        print(render_trade_plan(context.trade_plan, getattr(context, "metadata", {}).get("final_decision")))
    return 0


def main(pipeline: AnalysisPipeline | None = None) -> int:
    args = build_parser().parse_args()
    if pipeline is None:
        pipeline, _, _ = build_application()
    return run_cli(
        args.ticker,
        pipeline,
        capital=args.capital,
        risk_pct=args.risk_pct,
        max_position_pct=args.max_position_pct,
    )


if __name__ == "__main__":
    raise SystemExit(main())
