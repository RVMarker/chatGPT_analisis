"""Integration boundary for the V11/V12 fundamental, valuation and risk engines."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any, Iterable
from investment_analyzer.analysis.fundamental.fundamental_engine import FundamentalEngine
from investment_analyzer.analysis.risk.risk_engine import RiskEngine
from investment_analyzer.analysis.valuation.dcf_engine import DCFEngine, DCFResult
from investment_analyzer.analysis.valuation.reit_engine import REITValuationEngine
from investment_analyzer.common.models import FinancialStatements, PriceData
from investment_analyzer.providers.provenance import DataPoint
from investment_analyzer.providers.provider_confidence import ProviderConfidence

@dataclass(slots=True)
class IntegratedFinancialAnalysis:
    fundamental: dict[str, Any]
    valuation: dict[str, Any]
    risk: dict[str, Any]
    strengths: list[str]
    red_flags: list[str]
    provider_validation: dict[str, dict[str, Any]] | None = None
    data_quality_score: float = 100.0
    blocked_fields: list[str] | None = None
    def as_dict(self): return asdict(self)

class FinancialAnalysisIntegrator:
    def __init__(self, fundamental=None, valuation=None, risk=None, reit_valuation=None, provider_confidence=None):
        self.fundamental = fundamental or FundamentalEngine()
        self.valuation = valuation or DCFEngine()
        self.risk = risk or RiskEngine()
        self.reit_valuation = reit_valuation or REITValuationEngine()
        self.provider_confidence = provider_confidence or ProviderConfidence()

    @staticmethod
    def _points(extra: Iterable[DataPoint] | None, field: str, value, provider="normalized", quality="MEDIUM"):
        points = list(extra or [])
        if value is not None and not any(p.field == field and p.provider == provider for p in points):
            points.append(DataPoint(field, value, provider, quality=quality))
        return points

    def run(self, statements: FinancialStatements, price: PriceData, *, growth_rates=None, wacc=None,
            terminal_growth=None, net_debt=None, asset_type=None, reit_required_yield=.09,
            reit_growth=.03, provider_points: Iterable[DataPoint] | None = None):
        if price.current <= 0: raise ValueError("El precio actual debe ser positivo")
        fundamental = self.fundamental.calculate(statements)
        balance, income, cashflow = statements.balance, statements.income, statements.cashflow
        debt = net_debt if net_debt is not None else float(balance.long_term_debt or 0) - float(balance.cash or 0)
        is_reit = str(asset_type or "").upper() in {"REIT", "FIBRA"}
        points = list(provider_points or [])
        raw_values = {
            "ffo": cashflow.ffo_official if cashflow.ffo_official is not None else cashflow.ffo_proxy,
            "affo": cashflow.affo_official, "ebitda": income.ebitda, "net_debt": debt,
            "interest_expense": income.interest_expense, "property_value": balance.property_value,
            "shares_outstanding": price.shares_outstanding, "distribution": cashflow.dividends_paid,
        }
        qualities = {"ffo": "HIGH" if cashflow.ffo_official is not None else "LOW_MEDIUM", "affo": "HIGH", "ebitda": "MEDIUM", "net_debt": "MEDIUM", "interest_expense": "MEDIUM", "property_value": "MEDIUM", "shares_outstanding": "MEDIUM", "distribution": "MEDIUM"}
        for field, value in raw_values.items(): points = self._points(points, field, value, quality=qualities[field])
        validation = self.provider_confidence.decide(points, raw_values.keys())
        blocked = [f for f, d in validation.items() if not d.vote_allowed and d.status != "MISSING"]
        data_quality_score = self.provider_confidence.score(validation)
        risk = self.risk.calculate(statements, market_value_equity=price.market_cap, is_reit=is_reit)
        valuation_warnings = []
        if price.shares_outstanding_source == "yahoo_fast_info_reconciled": valuation_warnings.append("Shares outstanding reconciliadas contra market cap/precio de Yahoo; escala aplicada: %g" % price.shares_outstanding_scale)
        elif price.shares_outstanding_source == "market_cap/current_price": valuation_warnings.append("Shares outstanding derivadas de market cap/precio del mismo proveedor")
        if is_reit and price.shares_outstanding:
            ffo_decision = validation["ffo"]
            affo_decision = validation["affo"]
            distribution_decision = validation["distribution"]
            property_decision = validation["property_value"]
            if ffo_decision.vote_allowed and ffo_decision.value is not None:
                affo = affo_decision.value if affo_decision.vote_allowed else None
                distribution = distribution_decision.value if distribution_decision.vote_allowed else None
                property_value = property_decision.value if property_decision.vote_allowed else None
                source_quality = "FFO_OFFICIAL" if cashflow.ffo_official is not None else "FFO_PROXY"
                reit = self.reit_valuation.calculate(ffo=float(ffo_decision.value), shares_outstanding=float(price.shares_outstanding), current_price=float(price.current), required_yield=reit_required_yield, growth=reit_growth, source_quality=source_quality, affo=affo, distribution=distribution, distribution_period=cashflow.dividends_paid_period, distribution_source=cashflow.distribution_source, property_value=property_value, net_debt=validation["net_debt"].value if validation["net_debt"].vote_allowed else None, ebitda=validation["ebitda"].value if validation["ebitda"].vote_allowed else None, interest_expense=validation["interest_expense"].value if validation["interest_expense"].vote_allowed else None)
                valuation = reit.as_dict()
                valuation.update({"model": reit.method, "provider_validation": {k: v.__dict__ for k,v in validation.items()}, "blocked_fields": blocked, "assumptions": {"required_yield": reit_required_yield, "growth": reit_growth}})
                valuation_warnings.extend(reit.warnings)
            else:
                valuation = {"available": False, "score": None, "model": "FFO_CAPITALIZATION", "warnings": ["FIBRA/REIT: FFO bloqueado por conflicto/falta de fuente confiable; valoración no vota"], "blocked_fields": blocked}
        elif growth_rates and wacc is not None and terminal_growth is not None and cashflow.free_cash_flow is not None:
            fcf_decision = validation.get("free_cash_flow")
            if fcf_decision is None or fcf_decision.vote_allowed:
                dcf: DCFResult = self.valuation.calculate(fcf_base=float(cashflow.free_cash_flow), growth_rates=growth_rates, wacc=float(wacc), terminal_growth=float(terminal_growth), net_debt=debt, shares_outstanding=price.shares_outstanding, current_price=price.current)
                valuation = dcf.as_dict(); valuation["available"] = dcf.fair_value_per_share is not None; valuation["score"] = REITValuationEngine._score(dcf.margin_of_safety) if dcf.margin_of_safety is not None else None; valuation_warnings.extend(dcf.warnings)
            else: valuation = {"available": False, "score": None, "warnings": ["FCF bloqueado por conflicto de fuentes"]}
        else:
            valuation = {"available": False, "score": None, "warnings": ["Valuation no ejecutada: faltan datos/modelo específico"]}
        strengths = list(dict.fromkeys(fundamental.strengths + risk.strengths))
        red_flags = list(dict.fromkeys(fundamental.red_flags + risk.red_flags + valuation_warnings + valuation.get("warnings", [])))
        if blocked: red_flags.append("Campos bloqueados por conflicto de proveedores: " + ", ".join(blocked))
        return IntegratedFinancialAnalysis(fundamental=fundamental.as_dict(), valuation=valuation, risk=risk.as_dict(), strengths=strengths, red_flags=red_flags, provider_validation={k: asdict(v) for k,v in validation.items()}, data_quality_score=data_quality_score, blocked_fields=blocked)
