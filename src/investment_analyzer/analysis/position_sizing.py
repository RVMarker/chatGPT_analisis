"""V12.86 position sizing from portfolio risk budget."""
from __future__ import annotations
from typing import Any

class PositionSizer:
    def calculate(self, *, capital: float, entry: float, stop_loss: float,
                  risk_pct: float=0.02, max_position_pct: float=1.0,
                  lot_size: int=1) -> dict[str, Any]:
        if capital <= 0 or entry <= 0 or stop_loss <= 0 or entry <= stop_loss:
            return {'status':'INSUFFICIENT_DATA','units':0,'risk_budget':None,'position_value':None}
        if not 0 < risk_pct <= 1: raise ValueError('risk_pct must be between 0 and 1')
        if not 0 < max_position_pct <= 1: raise ValueError('max_position_pct must be between 0 and 1')
        if lot_size < 1: raise ValueError('lot_size must be >= 1')
        budget=capital*risk_pct; risk_per_unit=entry-stop_loss
        raw_units=budget/risk_per_unit
        units=int(raw_units//lot_size*lot_size)
        cap_units=int((capital*max_position_pct)/entry//lot_size*lot_size)
        units=min(units,cap_units)
        value=units*entry; actual_risk=units*risk_per_unit
        return {'status':'OK' if units>0 else 'NO_POSITION','capital':capital,'risk_pct':risk_pct,'risk_budget':round(budget,2),'entry':entry,'stop_loss':stop_loss,'risk_per_unit':round(risk_per_unit,6),'units':units,'position_value':round(value,2),'position_pct':round(value/capital*100,2),'actual_risk':round(actual_risk,2),'actual_risk_pct':round(actual_risk/capital*100,2),'unused_risk_budget':round(budget-actual_risk,2),'max_position_pct':max_position_pct,'lot_size':lot_size}
