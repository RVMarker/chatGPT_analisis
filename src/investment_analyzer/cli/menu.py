"""Interactive menu for the V12 investment analyzer."""
from __future__ import annotations


def ask(prompt, default=None):
    value=input(prompt).strip()
    return value if value else default


def choose_analysis():
    print("\nTIPO DE ANALISIS")
    print("  1. Informe completo")
    print("  2. Solo decisión estratégica")
    print("  3. Solo decisión táctica")
    print("  4. Salir")
    while True:
        value=input("Seleccione una opción [1]: ").strip() or "1"
        if value in {"1","2","3","4"}: return value
        print("Opción no válida.")


def collect_instrument():
    while True:
        symbol=input("\nTicker / activo a analizar: ").strip()
        if symbol:return symbol.upper()
        print("Debe introducir un ticker o identificador.")


def run_interactive():
    print("="*72)
    print(" V12 — SISTEMA DE DECISIÓN DE INVERSIÓN")
    print(" Acciones | ETFs | REITs | FIBRAs | Cripto | Bonos")
    print("="*72)
    symbol=collect_instrument()
    option=choose_analysis()
    return {"symbol":symbol,"analysis_mode":{"1":"FULL","2":"STRATEGIC","3":"TACTICAL","4":"EXIT"}[option]}
