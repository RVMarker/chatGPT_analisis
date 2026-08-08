"""V12.27 CLI entry point for the multi-asset investment analyzer.

Usage:
    python orchestrator.py FMTY14.MX
    python orchestrator.py SPY
    python orchestrator.py BTC-USD
    python orchestrator.py CETES28

Provider-specific data acquisition remains delegated to the existing provider
layer; this CLI is deliberately an orchestration boundary.
"""
from __future__ import annotations
import argparse
import json
import sys
from investment_analyzer.pipeline.end_to_end import InvestmentPipeline


def build_parser():
    p=argparse.ArgumentParser(description="V12 Investment Decision Engine")
    p.add_argument("symbol",help="Ticker o identificador del instrumento")
    p.add_argument("--asset-type",choices=["STOCK","ETF","REIT","FIBRA","CRYPTO","BOND"])
    p.add_argument("--isin")
    p.add_argument("--country")
    p.add_argument("--exchange")
    p.add_argument("--currency")
    p.add_argument("--provider-symbol",action="append",default=[],metavar="PROVIDER=SYMBOL")
    p.add_argument("--json",action="store_true",help="Emitir JSON")
    return p


def parse_provider_symbols(items):
    result={}
    for item in items:
        if "=" not in item: raise ValueError(f"Formato inválido: {item}; use PROVIDER=SYMBOL")
        provider,symbol=item.split("=",1)
        result[provider.strip().lower()]=symbol.strip()
    return result


def main(argv=None):
    args=build_parser().parse_args(argv)
    try:
        pipeline=InvestmentPipeline()
        result=pipeline.run(symbol=args.symbol,asset_type=args.asset_type,isin=args.isin,country=args.country,exchange=args.exchange,currency=args.currency,provider_symbols=parse_provider_symbols(args.provider_symbol))
        payload=result.as_dict()
        if args.json:
            print(json.dumps(payload,ensure_ascii=False,indent=2,default=str))
        else:
            c=payload["classification"]; d=payload["decision"]; q=payload["quality"]
            print("="*72); print("V12 — INFORME DE DECISIÓN DE INVERSIÓN"); print("="*72)
            print(f"Activo       : {args.symbol}")
            print(f"Clase        : {c['asset_type']} ({c['confidence']:.1f}% confianza)")
            print(f"Identidad    : {payload['identity']['canonical_id']}")
            print(f"Estratégico  : {d['strategic']['verdict']} | score={d['strategic']['score']} | cobertura={d['strategic']['coverage']:.1f}% | confianza={d['strategic']['confidence']:.1f}%")
            print(f"Táctico      : {d['tactical']['verdict']} | score={d['tactical']['score']} | cobertura={d['tactical']['coverage']:.1f}% | confianza={d['tactical']['confidence']:.1f}%")
            print(f"Calidad datos: {q['data_quality']:.1f}%")
            if q['blocked_fields']: print("Campos bloqueados: "+", ".join(q['blocked_fields']))
            for warning in payload["warnings"]: print("ADVERTENCIA: "+warning)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}",file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
