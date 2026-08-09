"""V12 CLI entrypoint over the existing AnalysisPipeline."""
from __future__ import annotations

from investment_analyzer.app import build_application
from investment_analyzer.analysis.decision.trade_plan import build_trade_plan
from investment_analyzer.analysis.decision.scenario_adapter import normalize_scenarios

STRATEGIC_WEIGHTS = {"fundamental": .35, "valuation": .30, "technical": .20, "risk": .15}
TACTICAL_WEIGHTS = {"technical": .45, "sentiment": .30, "smart_money": .25}


def _score(value):
    if isinstance(value, dict):
        if value.get("available") is False:
            return None
        for key in ("score", "total_score", "normalized_score", "rating"):
            if key in value:
                value = value[key]
                break
    try:
        return max(0.0, min(100.0, float(value))) if value is not None else None
    except (TypeError, ValueError):
        return None


def _weighted(values, weights):
    available = [(k, _score(values.get(k)), w) for k, w in weights.items()]
    available = [(k, s, w) for k, s, w in available if s is not None]
    if not available:
        return None, 0.0, {}
    total_weight = sum(w for _, _, w in available)
    score = sum(s * w for _, s, w in available) / total_weight
    breakdown = {k: {"score": s, "weight": w / total_weight, "contribution": s * w / total_weight} for k, s, w in available}
    return round(score, 2), round(100 * len(available) / len(weights), 2), breakdown


def _find(mapping, names):
    if not isinstance(mapping, dict):
        return None
    wanted = {str(x).lower() for x in names}
    for k, v in mapping.items():
        if str(k).lower() in wanted:
            try:
                value = float(v)
                if value > 0:
                    return value
            except (TypeError, ValueError):
                pass
    for v in mapping.values():
        if isinstance(v, dict):
            found = _find(v, names)
            if found is not None:
                return found
    return None


def _current_price(context):
    for source in (getattr(context, "price", None), getattr(context, "technical", None)):
        if isinstance(source, dict):
            value = _find(source, ("current", "close", "price", "last", "last_price"))
            if value is not None:
                return value
        else:
            for attr in ("current", "close", "price", "value"):
                value = getattr(source, attr, None)
                if value is not None:
                    try:
                        return float(value)
                    except (TypeError, ValueError):
                        pass
    return None


def _verdict(score):
    if score is None:
        return "N/D"
    if score >= 80: return "COMPRAR"
    if score >= 70: return "ACUMULAR"
    if score >= 50: return "MANTENER"
    if score >= 35: return "REDUCIR"
    return "VENDER"


def run():
    ticker = input("Activo a analizar: ").strip()
    if not ticker:
        raise SystemExit("Debe indicar un activo.")
    capital = float(input("Capital disponible [5000]: ") or "5000")
    risk_pct = float(input("Riesgo máximo por operación % [2]: ") or "2") / 100
    max_position_pct = float(input("Máximo por posición % [25]: ") or "25") / 100

    pipeline, _, _ = build_application()
    context = pipeline.run(ticker)

    strategic, strategic_coverage, strategic_breakdown = _weighted(
        {"fundamental": context.fundamentals, "valuation": context.valuation,
         "technical": context.technical, "risk": context.risk}, STRATEGIC_WEIGHTS)
    tactical, tactical_coverage, tactical_breakdown = _weighted(
        {"technical": context.technical, "sentiment": context.sentiment,
         "smart_money": context.metadata.get("smart_money")}, TACTICAL_WEIGHTS)

    price = _current_price(context)
    scenarios = normalize_scenarios(context.valuation or {})
    fair, bear, bull = scenarios["base"], scenarios["bear"], scenarios["bull"]

    technical = context.technical or {}
    support = _find(technical, ("support", "support_level", "nearest_support"))
    resistance = _find(technical, ("resistance", "resistance_level", "nearest_resistance"))
    atr = _find(technical, ("atr", "atr14", "average_true_range"))
    trade = build_trade_plan(price=price, fair_value=fair, bear_value=bear, bull_value=bull,
                             support=support, resistance=resistance, atr=atr,
                             capital=capital, risk_pct=risk_pct,
                             max_position_pct=max_position_pct)

    strategic_verdict = _verdict(strategic)
    tactical_verdict = _verdict(tactical)
    if strategic_verdict in {"VENDER", "REDUCIR"}:
        operation = "VENDER"
    elif trade["operation"] == "COMPRAR" and strategic_verdict in {"COMPRAR", "ACUMULAR", "MANTENER"}:
        operation = "COMPRAR"
    else:
        operation = "ESPERAR"

    print("\n" + "=" * 72)
    print("DECISIÓN DE INVERSIÓN V12")
    print("=" * 72)
    print(f"Activo:              {ticker.upper()}")
    print(f"Precio:              {price if price is not None else 'N/D'}")
    print(f"Estratégico:         {strategic_verdict} | {strategic if strategic is not None else 'N/D'} | cobertura {strategic_coverage:.1f}%")
    print(f"Táctico:             {tactical_verdict} | {tactical if tactical is not None else 'N/D'} | cobertura {tactical_coverage:.1f}%")
    print("\nVALORACIÓN")
    print(f"Bear Case:           {bear if bear is not None else 'N/D'}")
    print(f"Fair Value:          {fair if fair is not None else 'N/D'}")
    print(f"Bull Case:           {bull if bull is not None else 'N/D'}")
    print(f"Margin of Safety:    {trade.get('margin_of_safety_pct') if trade.get('margin_of_safety_pct') is not None else 'N/D'}%")
    print("\nPLAN OPERATIVO")
    for key, label in (("entry", "Entry"), ("stop_loss", "Stop Loss"), ("target_1", "Target 1"), ("target_2", "Target 2"), ("risk_reward", "R/R"), ("units", "Unidades"), ("position_value", "Inversión"), ("actual_risk", "Riesgo real")):
        print(f"{label + ':':20}{trade.get(key) if trade.get(key) is not None else 'N/D'}")
    print("\nOPERACIÓN FINAL:", operation)
    if trade.get("reasons"):
        print("Motivos para ESPERAR / bloquear:")
        for reason in trade["reasons"]:
            print(" -", reason)
    print("\nDesglose estratégico:", strategic_breakdown)
    print("Desglose táctico:   ", tactical_breakdown)
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
