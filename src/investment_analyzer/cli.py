"""V12.60 command-line entry point for the multi-asset investment analyzer."""
from __future__ import annotations
import argparse
from investment_analyzer.app import build_application
from investment_analyzer.pipeline.actionable_report import render_actionable_layer
from investment_analyzer.pipeline.decision_report import render_decision_report
from investment_analyzer.pipeline.multi_asset_cli_report import render_complete_report
from investment_analyzer.pipeline.pipeline import AnalysisPipeline

format_decision_report=render_decision_report

def build_parser()->argparse.ArgumentParser:
    p=argparse.ArgumentParser(description='V12 Investment Analyzer')
    p.add_argument('ticker',nargs='?',help='Ticker/activo, por ejemplo FMTY14.MX, AAPL, SPY, BTC-USD')
    return p

def run_cli(ticker:str,pipeline:AnalysisPipeline)->int:
    context=pipeline.run(ticker.strip().upper())
    print(format_decision_report(context)); print(render_complete_report(context)); print(render_actionable_layer(context)); return 0

def main(pipeline:AnalysisPipeline|None=None)->int:
    args=build_parser().parse_args(); ticker=(args.ticker or input('Ingrese el activo: ').strip()).upper()
    if not ticker: raise SystemExit('Debe indicar un activo.')
    if pipeline is None: pipeline,_,_=build_application()
    return run_cli(ticker,pipeline)

if __name__=='__main__': raise SystemExit(main())
