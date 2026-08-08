"""V12.30 interactive VS Code entry point integrated with the pipeline."""
from __future__ import annotations
import argparse,json,sys
from investment_analyzer.pipeline.end_to_end import InvestmentPipeline
from investment_analyzer.cli.menu import run_interactive

ASSET_TYPES=["STOCK","ETF","REIT","FIBRA","CRYPTO","BOND"]

def build_parser():
    p=argparse.ArgumentParser(description="V12 Investment Decision Engine")
    p.add_argument("symbol",nargs="?",help="Ticker; si se omite, se solicita interactivamente")
    p.add_argument("--asset-type",choices=ASSET_TYPES); p.add_argument("--isin"); p.add_argument("--country"); p.add_argument("--exchange"); p.add_argument("--currency")
    p.add_argument("--provider-symbol",action="append",default=[],metavar="PROVIDER=SYMBOL"); p.add_argument("--json",action="store_true"); p.add_argument("--once",action="store_true",help="Ejecutar una sola vez")
    return p

def parse_provider_symbols(items):
    result={}
    for item in items:
        if "=" not in item: raise ValueError(f"Formato inválido: {item}; use PROVIDER=SYMBOL")
        provider,symbol=item.split("=",1); result[provider.strip().lower()]=symbol.strip()
    return result

def render(payload):
    c,d,q=payload["classification"],payload["decision"],payload["quality"]
    print("\n"+"="*72); print("V12 — INFORME DE DECISIÓN DE INVERSIÓN"); print("="*72)
    print(f"Activo       : {payload['identity']['symbol']}"); print(f"Clase        : {c['asset_type']} ({c['confidence']:.1f}% confianza)"); print(f"Identidad    : {payload['identity']['canonical_id']}")
    for horizon in ("strategic","tactical"):
        x=d[horizon]; label="Estratégico" if horizon=="strategic" else "Táctico"
        print(f"{label:<12}: {x['verdict']} | score={x['score']} | cobertura={x['coverage']:.1f}% | confianza={x['confidence']:.1f}%")
    print(f"Calidad datos: {q['data_quality']:.1f}% | Consenso: {q['consensus_quality']:.1f}%")
    if q["blocked_fields"]: print("Campos bloqueados: "+", ".join(q["blocked_fields"]))
    for warning in payload["warnings"]: print("ADVERTENCIA: "+warning)

def execute(symbol,args,mode):
    pipeline=InvestmentPipeline()
    result=pipeline.run(symbol=symbol,asset_type=args.asset_type,isin=args.isin,country=args.country,exchange=args.exchange,currency=args.currency,provider_symbols=parse_provider_symbols(args.provider_symbol))
    payload=result.as_dict()
    if mode=="STRATEGIC": payload["decision"]["tactical"]={"verdict":"NO EJECUTADO","score":None,"coverage":0,"confidence":0}
    elif mode=="TACTICAL": payload["decision"]["strategic"]={"verdict":"NO EJECUTADO","score":None,"coverage":0,"confidence":0}
    return payload

def main(argv=None):
    args=build_parser().parse_args(argv)
    try:
        if args.symbol:
            payload=execute(args.symbol,args,"FULL")
            if args.json: print(json.dumps(payload,ensure_ascii=False,indent=2,default=str))
            else: render(payload)
            return 0
        while True:
            selection=run_interactive(); mode=selection["analysis_mode"]
            if mode=="EXIT": return 0
            payload=execute(selection["symbol"],args,mode)
            if args.json: print(json.dumps(payload,ensure_ascii=False,indent=2,default=str))
            else: render(payload)
            again=input("\n¿Analizar otro activo? [S/n]: ").strip().lower()
            if again in {"n","no"}: return 0
    except (KeyboardInterrupt,EOFError): print("\nAnálisis cancelado."); return 0
    except Exception as exc: print(f"ERROR: {exc}",file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
