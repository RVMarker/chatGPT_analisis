"""Executable V12 trade-plan calculations used by the real analysis pipeline."""
from __future__ import annotations


def _num(value):
    try:
        value = float(value)
        return value if value > 0 else None
    except (TypeError, ValueError):
        return None


def build_trade_plan(*, price, fair_value=None, bear_value=None, bull_value=None,
                     support=None, resistance=None, atr=None, capital=5000.0,
                     risk_pct=0.02, max_position_pct=0.25, min_rr=2.0,
                     min_mos_pct=10.0):
    price = _num(price); fair = _num(fair_value); bear = _num(bear_value); bull = _num(bull_value)
    support = _num(support); resistance = _num(resistance); atr = _num(atr)
    capital = _num(capital) or 0.0
    if not price:
        return {"available": False, "operation": "ESPERAR", "reasons": ["Precio actual no disponible"]}

    stop_loss = support if support and support < price else None
    if stop_loss is None and atr and price - 2.0 * atr > 0:
        stop_loss = price - 2.0 * atr
        stop_method = "2x_ATR"
    else:
        stop_method = "20_period_support" if stop_loss else None

    target_2 = fair if fair and fair > price else None
    if target_2 is None and bull and bull > price:
        target_2 = bull
    if bull and target_2:
        target_2 = min(target_2, bull)

    risk_per_unit = price - stop_loss if stop_loss else None
    # Target 1 is deliberately a real market resistance. We do not manufacture
    # a synthetic 1R target just to make the Quality Gate pass.
    target_1 = resistance if resistance and resistance > price else None
    target_1_method = "20_period_resistance" if target_1 else None
    if target_1 and target_2 and target_1 >= target_2:
        target_1 = None
        target_1_method = None

    mos = ((fair - price) / fair * 100.0) if fair else None
    rr = ((target_2 - price) / risk_per_unit) if target_2 and risk_per_unit and risk_per_unit > 0 else None
    risk_budget = capital * float(risk_pct)
    max_position_value = capital * float(max_position_pct)
    units_by_risk = int(risk_budget / risk_per_unit) if risk_per_unit and risk_per_unit > 0 else 0
    units_by_capital = int(max_position_value / price) if price else 0
    units = max(0, min(units_by_risk, units_by_capital))
    actual_risk = units * risk_per_unit if risk_per_unit else None

    reasons = []
    if stop_loss is None: reasons.append("Stop Loss no disponible")
    if target_1 is None: reasons.append("Target 1 no disponible")
    if target_2 is None: reasons.append("Target 2 no disponible")
    if mos is None or mos < float(min_mos_pct): reasons.append(f"Margin of Safety inferior a {float(min_mos_pct):.1f}%")
    if rr is None or rr < float(min_rr): reasons.append(f"R/R no disponible o inferior a {float(min_rr):.1f}")
    if units <= 0: reasons.append("Tamaño de posición no permitido por riesgo/capital")

    return {
        "available": not reasons, "operation": "COMPRAR" if not reasons else "ESPERAR", "reasons": reasons,
        "entry": price, "stop_loss": stop_loss, "stop_method": stop_method,
        "target_1": target_1, "target_1_method": target_1_method, "target_2": target_2,
        "bear_value": bear, "base_fair_value": fair, "bull_value": bull,
        "margin_of_safety_pct": mos, "risk_per_unit": risk_per_unit,
        "risk_budget": risk_budget, "units": units, "position_value": units * price,
        "actual_risk": actual_risk, "risk_reward": rr,
    }
