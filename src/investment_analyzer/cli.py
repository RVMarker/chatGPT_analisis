"""Command-line entry point for the V11 investment analyzer."""
from __future__ import annotations

import argparse

from investment_analyzer.app import build_application
from investment_analyzer.pipeline.decision_report import render_decision_report
from investment_analyzer.pipeline.pipeline import AnalysisPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="V11 Investment Analyzer")
    parser.add_argument("ticker", help="Ticker canónico, por ejemplo FMTY14.MX")
    return parser


def run_cli(ticker: str, pipeline: AnalysisPipeline) -> int:
    context = pipeline.run(ticker)
    print(render_decision_report(context))
    return 0


def main(pipeline: AnalysisPipeline | None = None) -> int:
    args = build_parser().parse_args()
    if pipeline is None:
        pipeline, _, _ = build_application()
    return run_cli(args.ticker, pipeline)


if __name__ == "__main__":
    raise SystemExit(main())
