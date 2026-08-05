"""DCF valuation engine V11.

Deterministic, auditable FCFF DCF. It does not fetch market data: callers
provide normalized assumptions so the same engine can be replayed historically.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class DCFResult:
    enterprise_value: float
    equity_value: float
    fair_value_per_share: float | None
    margin_of_safety: float | None
    wacc: float
    terminal_growth: float
    assumptions: dict[str, Any]
    warnings: list[str]

    def as_dict(self):
        return asdict(self)


class DCFEngine:
    """FCFF DCF with explicit sanity checks and sensitivity support."""

    @staticmethod
    def _validate_rate(name: str, value: float, minimum: float = -0.99):
        value = float(value)
        if value <= minimum:
            raise ValueError(f"{name} fuera de rango: {value}")
        return value

    def calculate(
        self,
        fcf_base: float,
        growth_rates: list[float],
        wacc: float,
        terminal_growth: float,
        net_debt: float = 0.0,
        shares_outstanding: float | None = None,
        current_price: float | None = None,
    ) -> DCFResult:
        if not growth_rates:
            raise ValueError("growth_rates no puede estar vacío")
        if fcf_base < 0:
            raise ValueError("FCFF base negativo requiere un modelo específico de turnaround")
        wacc = self._validate_rate("WACC", wacc)
        terminal_growth = self._validate_rate("terminal_growth", terminal_growth)
        if wacc <= terminal_growth:
            raise ValueError("WACC debe ser mayor que el crecimiento terminal")

        fcf = float(fcf_base)
        pv = 0.0
        projected = []
        for year, growth in enumerate(growth_rates, start=1):
            growth = self._validate_rate("growth", growth)
            fcf *= 1.0 + growth
            discounted = fcf / ((1.0 + wacc) ** year)
            pv += discounted
            projected.append({"year": year, "growth": growth, "fcff": fcf, "pv": discounted})

        terminal_fcf = fcf * (1.0 + terminal_growth)
        terminal_value = terminal_fcf / (wacc - terminal_growth)
        pv_terminal = terminal_value / ((1.0 + wacc) ** len(growth_rates))
        enterprise_value = pv + pv_terminal
        equity_value = enterprise_value - float(net_debt)

        fair_value = None
        margin = None
        warnings: list[str] = []
        if shares_outstanding and shares_outstanding > 0:
            fair_value = equity_value / float(shares_outstanding)
            if current_price is not None and current_price > 0:
                margin = fair_value / float(current_price) - 1.0
        if terminal_growth >= wacc - 0.02:
            warnings.append("Valoración muy sensible: crecimiento terminal se aproxima al WACC")
        if terminal_value / enterprise_value > 0.75:
            warnings.append("Más del 75% del EV procede del valor terminal")

        return DCFResult(
            enterprise_value=enterprise_value,
            equity_value=equity_value,
            fair_value_per_share=fair_value,
            margin_of_safety=margin,
            wacc=wacc,
            terminal_growth=terminal_growth,
            assumptions={"fcf_base": fcf_base, "growth_rates": growth_rates, "net_debt": net_debt, "projected": projected},
            warnings=warnings,
        )

    def sensitivity(
        self,
        fcf_base: float,
        growth_rates: list[float],
        wacc_values: list[float],
        terminal_growth_values: list[float],
        net_debt: float = 0.0,
        shares_outstanding: float | None = None,
    ) -> list[dict[str, float]]:
        rows = []
        for wacc in wacc_values:
            for growth in terminal_growth_values:
                result = self.calculate(fcf_base, growth_rates, wacc, growth, net_debt, shares_outstanding)
                rows.append({"wacc": wacc, "terminal_growth": growth, "fair_value_per_share": result.fair_value_per_share or float("nan")})
        return rows
