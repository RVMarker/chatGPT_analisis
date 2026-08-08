"""V12.28 interactive VS Code CLI entry point."""
from __future__ import annotations
import argparse
import json
import sys
from investment_analyzer.pipeline.end_to_end import InvestmentPipeline

ASSET_TYPES=["STOCK","ETF","REIT","FIBRA","CRYPTO","BOND"]

def build_parser():
    p=argparse.ArgumentParser(description="V12 Investment Decision Engine")
    p.add_argument("symbol",nargs="?",help="Ticker; si se omite, se solicita interactivamente")
    p.add_argument("--asset-type",choices=ASSET_TYPES)
    p.add_argument("--isin"); p.add_argument("--country"); p.add_argument("--exchange"); p.add_argument("--currency")
    p.add_argument("--provider-symbol",action="append",default=[],metavar="PROVIDER=SYMBOL")
    p.add_argument("--json",action="store_true")
    return p

def parse_provider_symbols(items):
    result={}
    for item in items:
        if "=" not in item: raise ValueError(f"Formato inválido: {item}; use PROVIDER=SYMBOL")
        provider,symbol=item.split("=",1); result[provider.strip().lower()]=symbol.strip()
    return result

def ask_symbol():
    while True:
        try: value=input("\nTicker / activo a analizar: ").strip()
        except (EOFError,KeyboardInterrupt): print("\nAnálisis cancelado."); return None
        if value:return value
        print("Debe introducir un ticker o identificador.")

def main(argv=None):
    args=build_parser().parse_args(argv)
    symbol=args.symbol or ask_symbol()
    if not symbol:return 0
    try:
        pipeline=InvestmentPipeline()
        result=pipeline.run(symbol=symbol,asset_type=args.asset_type,isin=args.isin,country=args.country,exchange=args.exchange,currency=args.currency,provider_symbols=parse_provider_symbols(args.provider_symbol))
        payload=result.as_dict()
        if args.json:
            print(json.dumps(payload,ensure_ascii=False,indent=2,default=str)); return 0
        c=payload["classification"]; d=payload["decision"]; q=payload["quality"]
        print("\n"+"="*72); print("V12 — INFORME DE DECISIÓN DE INVERSIÓN"); print("="*72)
        print(f"Activo       : {symbol}")
        print(f"Clase        : {c['asset_type']} ({c['confidence']:.1f}% confianza)")
        print(f"Identidad    : {payload['identity']['canonical_id']}")
        print(f"Estratégico  : {d['strategic']['verdict']} | score={d['strategic']['score']} | cobertura={d['strategic']['coverage']:.1f}% | confianza={d['strategic']['confidence']:.1f}%")
        print(f"Táctico      : {d['tactical']['verdict']} | score={d['tactical']['score']} | cobertura={d['tactical']['coverage']:.1f}% | confianza={d['tactical']['confidence']:.1f}%")
        print(f"Calidad datos: {q['data_quality']:.1f}%")
        if q['blocked_fields']:print("Campos bloqueados: "+", ".join(q['blocked_fields']))
        for warning in payload["warnings"]:print("ADVERTENCIA: "+warning)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}",file=sys.stderr); return 2

if __name__=="__main__":raise SystemExit(main())
