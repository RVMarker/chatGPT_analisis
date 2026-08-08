"""REIT/FIBRA valuation engine V11.3.

Valuation is deliberately separated from risk. FFO/AFFO determine value;
leverage and interest coverage remain risk diagnostics and do not get counted
twice inside the valuation score.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass

@dataclass(slots=True)
class REITValuationResult:
    available: bool
    method: str
    ffo_per_share: float | None
    fair_value_per_share: float | None
    margin_of_safety: float | None
    score: float | None
    required_yield: float
    growth: float
    source_quality: str
    warnings: list[str]
    valuation_quality: str = "LOW"
    affo_per_share: float | None = None
    affo_fair_value_per_share: float | None = None
    distribution_per_share: float | None = None
    payout_ratio: float | None = None
    distribution_period: str | None = None
    distribution_source: str | None = None
    nav_per_share: float | None = None
    cap_rate: float | None = None
    net_debt_to_ebitda: float | None = None
    interest_coverage: float | None = None
    component_scores: dict[str, float] | None = None
    component_coverage: float = 0.0
    def as_dict(self): return asdict(self)

class REITValuationEngine:
    @staticmethod
    def _rate(name, value):
        value = float(value)
        if not 0.0 <= value < 1.0: raise ValueError(f"{name} debe estar entre 0 y 1")
        return value
    @staticmethod
    def _score(margin):
        if margin is None: return None
        if margin >= .30: return 100.0
        if margin >= .20: return 90.0
        if margin >= .10: return 80.0
        if margin >= .00: return 70.0
        if margin >= -.10: return 55.0
        if margin >= -.20: return 40.0
        if margin >= -.30: return 25.0
        return 10.0
    @staticmethod
    def _quality(source_quality, affo_available=False, nav_available=False):
        source = (source_quality or "").upper()
        if source == "FFO_OFFICIAL" and affo_available: return "HIGH"
        if source == "FFO_OFFICIAL": return "MEDIUM_HIGH"
        if source in {"FFO_PROXY", "FFO_ESTIMATE"}: return "MEDIUM" if nav_available else "LOW_MEDIUM"
        return "LOW"
    @staticmethod
    def _normalize_period(period):
        if period is None: return None
        normalized = str(period).strip().lower().replace("-", "_")
        return {"year":"annual","yearly":"annual","fiscal_year":"annual","fy":"annual","quarter":"quarterly","month":"monthly"}.get(normalized, normalized)
    def _fair_value(self, per_share, required_yield, growth):
        if per_share is None or per_share <= 0: return None
        return per_share * (1 + growth) / (required_yield - growth)
    def calculate(self, *, ffo, shares_outstanding, current_price, required_yield=.09, growth=.03,
                  source_quality="FFO_PROXY", affo=None, distribution=None, distribution_period=None,
                  distribution_source=None, property_value=None, net_debt=None, ebitda=None, interest_expense=None):
        required_yield, growth = self._rate("required_yield", required_yield), self._rate("growth", growth)
        if required_yield <= growth: raise ValueError("required_yield debe ser mayor que growth")
        period = self._normalize_period(distribution_period)
        source = (source_quality or "").upper()
        ffo_valid = ffo is not None and float(ffo) > 0
        if shares_outstanding is None or float(shares_outstanding) <= 0 or current_price <= 0 or not ffo_valid:
            return REITValuationResult(False,"FFO_CAPITALIZATION",None,None,None,None,required_yield,growth,source_quality,["Faltan FFO positivo, acciones en circulación o precio actual válido"],self._quality(source_quality),distribution_period=period,distribution_source=distribution_source)
        shares = float(shares_outstanding)
        ffo_per_share = float(ffo) / shares
        affo_per_share = float(affo) / shares if affo is not None and float(affo) > 0 else None
        ffo_fair_value = self._fair_value(ffo_per_share, required_yield, growth)
        affo_fair_value = self._fair_value(affo_per_share, required_yield, growth)
        if affo_fair_value is not None and source == "FFO_OFFICIAL":
            fair_value = .50 * ffo_fair_value + .50 * affo_fair_value
            method = "FFO_AFFO_CAPITALIZATION"
        else:
            fair_value = ffo_fair_value
            method = "FFO_CAPITALIZATION"
        margin = fair_value / float(current_price) - 1
        base_score = self._score(margin)
        distribution_per_share = payout_ratio = None
        if distribution is not None and period == "annual" and distribution_source == "reit_distribution":
            distribution_per_share = abs(float(distribution)) / shares
            payout_ratio = distribution_per_share / ffo_per_share
        nav_per_share = float(property_value) / shares if property_value is not None and float(property_value) > 0 else None
        cap_rate = float(ffo) / float(property_value) if property_value is not None and float(property_value) > 0 else None
        net_debt_to_ebitda = float(net_debt) / float(ebitda) if net_debt is not None and ebitda is not None and float(ebitda) > 0 else None
        interest_coverage = float(ebitda) / abs(float(interest_expense)) if ebitda is not None and interest_expense not in (None, 0) else None
        components = {"ffo_value": base_score} if base_score is not None else {}
        if affo_fair_value is not None and source == "FFO_OFFICIAL": components["affo_value"] = self._score(affo_fair_value / float(current_price) - 1)
        score = round(sum(components.values()) / len(components), 2) if components else None
        valuation_quality = self._quality(source_quality, affo_available=affo_fair_value is not None, nav_available=nav_per_share is not None)
        warnings=[]
        if source != "FFO_OFFICIAL": warnings.append("FFO oficial no disponible; la valoración debe considerarse de menor confianza")
        if source == "FFO_PROXY": warnings.append("FFO PROXY: derivado de estados financieros; no sustituye FFO oficial de la FIBRA")
        if affo is None: warnings.append("AFFO oficial no disponible; no se infiere AFFO a partir de FCF/capex")
        if property_value is None: warnings.append("NAV/cap-rate no disponibles: falta valor de propiedades validado")
        if distribution is None: warnings.append("Payout sobre FFO no disponible: falta distribución trazable")
        elif distribution_source != "reit_distribution": warnings.append("Distribución no certificada como FIBRA/REIT; se excluye del cálculo de payout")
        elif period != "annual": warnings.append("Distribución no identificada como anual; se evita mezclar períodos")
        if net_debt_to_ebitda is None: warnings.append("Net debt/EBITDA REIT no disponible; queda N/D y no se inventa un dato")
        if interest_coverage is None: warnings.append("Cobertura de intereses REIT no disponible; queda N/D")
        if required_yield-growth < .04: warnings.append("Valoración sensible: spread entre yield requerido y crecimiento < 4pp")
        if margin < 0: warnings.append("Precio de mercado supera el valor razonable del modelo FFO/AFFO")
        return REITValuationResult(True,method,ffo_per_share,fair_value,margin,score,required_yield,growth,source_quality,warnings,valuation_quality,affo_per_share,affo_fair_value,distribution_per_share,payout_ratio,period,distribution_source,nav_per_share,cap_rate,net_debt_to_ebitda,interest_coverage,components,len(components)/2.0 if components else 0.0)
