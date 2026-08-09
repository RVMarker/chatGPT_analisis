"""Integration boundary for the V12 fundamental/valuation/risk engines."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any
from investment_analyzer.analysis.fundamental.fundamental_engine import FundamentalEngine
from investment_analyzer.analysis.risk.risk_engine import RiskEngine
from investment_analyzer.analysis.valuation.dcf_engine import DCFEngine, DCFResult
from investment_analyzer.analysis.valuation.reit_engine import REITValuationEngine
from investment_analyzer.common.models import FinancialStatements, PriceData

@dataclass(slots=True)
class IntegratedFinancialAnalysis:
    fundamental: dict[str, Any]; valuation: dict[str, Any]; risk: dict[str, Any]; strengths: list[str]; red_flags: list[str]
    def as_dict(self): return asdict(self)

class FinancialAnalysisIntegrator:
    """Run fundamental, valuation and risk once from normalized provider data.

    When explicit DCF assumptions are not supplied, the adapter derives them
    from the company's own historical FCF and market data. The assumptions are
    exposed in the result so the valuation is auditable rather than silently
    inventing a fair value.
    """
    DEFAULT_RISK_FREE = 0.04
    DEFAULT_EQUITY_RISK_PREMIUM = 0.055
    DEFAULT_TERMINAL_GROWTH = 0.025

    def __init__(self, fundamental=None, valuation=None, risk=None, reit_valuation=None):
        self.fundamental=fundamental or FundamentalEngine(); self.valuation=valuation or DCFEngine(); self.risk=risk or RiskEngine(); self.reit_valuation=reit_valuation or REITValuationEngine()

    @staticmethod
    def _growth_rates(historical_fcf: list[float], years: int = 5) -> tuple[list[float] | None, list[str]]:
        values = [float(x) for x in historical_fcf if x is not None and float(x) > 0]
        warnings: list[str] = []
        if len(values) < 2:
            return None, ["DCF no ejecutado: se requieren al menos 2 años de FCF positivo"]
        first, last = values[0], values[-1]
        periods = len(values) - 1
        cagr = (last / first) ** (1.0 / periods) - 1.0 if first > 0 and last > 0 else None
        if cagr is None:
            return None, ["DCF no ejecutado: no se pudo calcular CAGR de FCF"]
        # Use historical FCF CAGR as the anchor and fade it toward terminal growth.
        # Cap extreme historical growth so one anomalous year cannot dominate the DCF.
        anchor = max(-0.05, min(0.20, cagr))
        if abs(cagr - anchor) > 1e-9:
            warnings.append("CAGR histórico de FCF limitado a [-5%, 20%] para evitar extrapolación extrema")
        rates = [anchor * (1.0 - 0.18 * i) for i in range(years)]
        return rates, warnings

    @classmethod
    def _derive_wacc(cls, statements: FinancialStatements, price: PriceData, risk_free_rate=None):
        rf = float(risk_free_rate) if risk_free_rate is not None else cls.DEFAULT_RISK_FREE
        beta = float(price.beta) if price.beta and price.beta > 0 else 1.0
        cost_equity = rf + beta * cls.DEFAULT_EQUITY_RISK_PREMIUM
        debt = max(0.0, float(statements.balance.long_term_debt or 0.0))
        market_cap = max(0.0, float(price.market_cap or 0.0))
        total_capital = market_cap + debt
        if total_capital <= 0 or debt <= 0:
            return max(0.06, min(0.18, cost_equity)), {
                "risk_free_rate": rf,
                "beta": beta,
                "equity_risk_premium": cls.DEFAULT_EQUITY_RISK_PREMIUM,
                "cost_of_equity": cost_equity,
                "debt_weight": 0.0,
                "equity_weight": 1.0,
                "method": "CAPM_equity_only",
            }
        interest = abs(float(statements.income.interest_expense or 0.0))
        pretax = float(statements.income.pretax_income or 0.0)
        net_income = float(statements.income.net_income or 0.0)
        tax_rate = 1.0 - (net_income / pretax) if pretax > 0 and 0 <= net_income <= pretax else 0.21
        tax_rate = max(0.0, min(0.35, tax_rate))
        cost_debt = interest / debt if interest > 0 else rf + 0.015
        cost_debt = max(0.02, min(0.12, cost_debt))
        ew = market_cap / total_capital
        dw = debt / total_capital
        wacc = ew * cost_equity + dw * cost_debt * (1.0 - tax_rate)
        return max(0.06, min(0.18, wacc)), {
            "risk_free_rate": rf,
            "beta": beta,
            "equity_risk_premium": cls.DEFAULT_EQUITY_RISK_PREMIUM,
            "cost_of_equity": cost_equity,
            "pre_tax_cost_of_debt": cost_debt,
            "tax_rate": tax_rate,
            "debt_weight": dw,
            "equity_weight": ew,
            "method": "CAPM_WACC",
        }

    def run(self, statements: FinancialStatements, price: PriceData, *, growth_rates=None, wacc=None, terminal_growth=None, net_debt=None, asset_type=None, reit_required_yield=.09, reit_growth=.03, risk_free_rate=None):
        if price.current <= 0: raise ValueError("El precio actual debe ser positivo")
        fundamental=self.fundamental.calculate(statements); balance,income,cashflow=statements.balance,statements.income,statements.cashflow
        debt=net_debt if net_debt is not None else float(balance.long_term_debt or 0)-float(balance.cash or 0)
        risk=self.risk.calculate(statements,market_value_equity=price.market_cap); valuation_warnings=[]
        if price.shares_outstanding_source == "yahoo_fast_info_reconciled": valuation_warnings.append("Shares outstanding reconciliadas contra market cap/precio de Yahoo; escala aplicada: %g" % price.shares_outstanding_scale)
        elif price.shares_outstanding_source == "market_cap/current_price": valuation_warnings.append("Shares outstanding no disponibles en Yahoo; derivadas de market cap/precio del mismo proveedor")
        is_reit=str(asset_type or "").upper() in {"REIT","FIBRA"}
        if is_reit and price.shares_outstanding:
            ffo=cashflow.ffo_official if cashflow.ffo_official is not None else cashflow.ffo_proxy
            source_quality="FFO_OFFICIAL" if cashflow.ffo_official is not None else "FFO_PROXY"
            if ffo is not None:
                reit=self.reit_valuation.calculate(ffo=float(ffo),shares_outstanding=float(price.shares_outstanding),current_price=float(price.current),required_yield=reit_required_yield,growth=reit_growth,source_quality=source_quality,affo=cashflow.affo_official,distribution=cashflow.dividends_paid,distribution_period=cashflow.dividends_paid_period,distribution_source=cashflow.distribution_source,property_value=balance.property_value,net_debt=debt,ebitda=income.ebitda,interest_expense=income.interest_expense)
                valuation=reit.as_dict(); valuation.update({"model":"FFO_CAPITALIZATION","ffo_proxy":cashflow.ffo_proxy,"ffo_official":cashflow.ffo_official,"affo_official":cashflow.affo_official,"assumptions":{"required_yield":reit_required_yield,"growth":reit_growth},"shares_outstanding_raw":price.shares_outstanding_raw,"shares_outstanding_source":price.shares_outstanding_source,"shares_outstanding_scale":price.shares_outstanding_scale}); valuation_warnings.extend(reit.warnings)
            else: valuation={"available":False,"score":None,"model":"FFO_CAPITALIZATION","warnings":["FIBRA/REIT detectado pero no existe FFO disponible"]}
        else:
            derived = False
            assumption_warnings = []
            if growth_rates is None:
                growth_rates, assumption_warnings = self._growth_rates(getattr(cashflow, "historical_fcf", []))
                derived = growth_rates is not None
            if wacc is None and growth_rates is not None:
                wacc, wacc_assumptions = self._derive_wacc(statements, price, risk_free_rate)
                derived = True
            else:
                wacc_assumptions = {"method": "explicit"}
            if terminal_growth is None and growth_rates is not None:
                terminal_growth = min(self.DEFAULT_TERMINAL_GROWTH, max(-0.01, float(growth_rates[-1]) * 0.5))
                terminal_growth = max(-0.01, min(0.03, terminal_growth))
                wacc_assumptions["terminal_growth_method"] = "conservative_fade_of_historical_FCF_growth"
            fcf=cashflow.free_cash_flow
            if fcf is not None and growth_rates is not None and wacc is not None and terminal_growth is not None and price.shares_outstanding:
                dcf: DCFResult=self.valuation.calculate(fcf_base=float(fcf),growth_rates=growth_rates,wacc=float(wacc),terminal_growth=float(terminal_growth),net_debt=debt,shares_outstanding=price.shares_outstanding,current_price=price.current)
                valuation=dcf.as_dict(); valuation["available"]=dcf.fair_value_per_share is not None; valuation["score"]=REITValuationEngine._score(dcf.margin_of_safety) if dcf.margin_of_safety is not None else None; valuation["model"]="FCFF_DCF"; valuation["assumption_source"]="historical_provider_data_plus_explicit_model_defaults"; valuation["wacc_details"]=wacc_assumptions; valuation["historical_fcf"] = list(getattr(cashflow, "historical_fcf", [])); valuation_warnings.extend(assumption_warnings); valuation_warnings.extend(dcf.warnings)
            else:
                missing=[]
                if fcf is None: missing.append("free_cash_flow")
                if growth_rates is None: missing.append("historical_FCF_growth")
                if wacc is None: missing.append("wacc")
                if terminal_growth is None: missing.append("terminal_growth")
                if not price.shares_outstanding: missing.append("shares_outstanding")
                valuation={"available":False,"score":None,"model":"FCFF_DCF","warnings":["Valuation no ejecutada: faltan datos trazables: " + ", ".join(missing)]}
                valuation_warnings.extend(assumption_warnings)
        strengths=list(dict.fromkeys(fundamental.strengths+risk.strengths)); red_flags=list(dict.fromkeys(fundamental.red_flags+risk.red_flags+valuation_warnings+valuation.get("warnings",[])))
        return IntegratedFinancialAnalysis(fundamental=fundamental.as_dict(),valuation=valuation,risk=risk.as_dict(),strengths=strengths,red_flags=red_flags)
