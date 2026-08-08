"""REIT/FIBRA valuation engine V11."""
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
    valuation_quality: str = "MEDIUM"
    affo_per_share: float | None = None
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
    def _quality(source_quality):
        quality = (source_quality or "").upper()
        if quality in {"FFO_OFFICIAL", "AFFO_OFFICIAL", "AFFO"}: return "HIGH"
        if quality in {"FFO_PROXY", "FFO_ESTIMATE"}: return "MEDIUM"
        return "LOW"
    @staticmethod
    def _normalize_period(period):
        if period is None: return None
        normalized = str(period).strip().lower().replace("-", "_")
        return {"year":"annual","yearly":"annual","fiscal_year":"annual","fy":"annual",
                "quarter":"quarterly","month":"monthly"}.get(normalized, normalized)
    @staticmethod
    def _leverage_score(value):
        if value is None: return None
        if value <= 2: return 100.0
        if value <= 3: return 85.0
        if value <= 4: return 70.0
        if value <= 5: return 50.0
        if value <= 6: return 30.0
        return 10.0
    @staticmethod
    def _coverage_score(value):
        if value is None: return None
        if value >= 6: return 100.0
        if value >= 4: return 85.0
        if value >= 3: return 70.0
        if value >= 2: return 50.0
        if value >= 1: return 25.0
        return 10.0
    @staticmethod
    def _payout_score(value):
        if value is None: return None
        if value <= .70: return 100.0
        if value <= .85: return 90.0
        if value <= 1: return 75.0
        if value <= 1.10: return 50.0
        return 20.0

    def calculate(self, *, ffo, shares_outstanding, current_price, required_yield=.09, growth=.03,
                  source_quality="FFO_PROXY", affo=None, distribution=None, distribution_period=None,
                  distribution_source=None, property_value=None, net_debt=None, ebitda=None, interest_expense=None):
        required_yield, growth = self._rate("required_yield", required_yield), self._rate("growth", growth)
        valuation_quality = self._quality(source_quality)
        period = self._normalize_period(distribution_period)
        if required_yield <= growth: raise ValueError("required_yield debe ser mayor que growth")
        if shares_outstanding <= 0 or current_price <= 0:
            return REITValuationResult(False,"FFO_CAPITALIZATION",None,None,None,None,required_yield,growth,source_quality,["Faltan acciones en circulación o precio actual válido"],valuation_quality,distribution_period=period,distribution_source=distribution_source)
        if ffo <= 0:
            return REITValuationResult(False,"FFO_CAPITALIZATION",None,None,None,None,required_yield,growth,source_quality,["FFO no positivo; no se puede capitalizar de forma robusta"],valuation_quality,distribution_period=period,distribution_source=distribution_source)
        ffo_per_share = float(ffo)/float(shares_outstanding)
        fair_value = ffo_per_share*(1+growth)/(required_yield-growth)
        margin = fair_value/float(current_price)-1
        affo_per_share = float(affo)/float(shares_outstanding) if affo is not None else None
        distribution_per_share = payout_ratio = None
        # Cash Dividends Paid from Yahoo is not automatically a FIBRA distribution.
        # It can vote only when the provider explicitly identifies it as the REIT distribution.
        if distribution is not None and period == "annual" and distribution_source == "reit_distribution":
            distribution_per_share = abs(float(distribution))/float(shares_outstanding)
            payout_ratio = distribution_per_share/ffo_per_share
        nav_per_share = float(property_value)/float(shares_outstanding) if property_value is not None and property_value > 0 else None
        cap_rate = float(ffo)/float(property_value) if property_value is not None and property_value > 0 else None
        net_debt_to_ebitda = float(net_debt)/float(ebitda) if net_debt is not None and ebitda and ebitda > 0 else None
        interest_coverage = float(ebitda)/abs(float(interest_expense)) if ebitda and interest_expense and interest_expense != 0 else None
        components = {}
        base = self._score(margin)
        if base is not None: components["ffo_value"] = base
        payout = self._payout_score(payout_ratio)
        if payout is not None: components["payout"] = payout
        leverage = self._leverage_score(net_debt_to_ebitda)
        if leverage is not None: components["leverage"] = leverage
        coverage_score = self._coverage_score(interest_coverage)
        if coverage_score is not None: components["interest_coverage"] = coverage_score
        score = base
        if len(components) > 1:
            weights={"ffo_value":.60,"payout":.15,"leverage":.15,"interest_coverage":.10}
            active=[(k,v,weights[k]) for k,v in components.items()]
            total=sum(x[2] for x in active)
            score=sum(v*w for _,v,w in active)/total
        warnings=[]
        if source_quality == "FFO_PROXY": warnings.append("FFO PROXY: derivado de estados financieros; no sustituye AFFO/FFO oficial de la FIBRA")
        if valuation_quality != "HIGH": warnings.append(f"Calidad de valoración {valuation_quality}: el valor razonable depende de la calidad del FFO disponible")
        if affo is None: warnings.append("AFFO oficial no disponible; no se infiere AFFO a partir de FCF/capex")
        if property_value is None: warnings.append("NAV/cap-rate no disponibles: falta valor de propiedades validado")
        if distribution is None: warnings.append("Payout sobre FFO no disponible: falta distribución/dividendos trazables")
        elif distribution_source != "reit_distribution": warnings.append("Payout sobre FFO no disponible: Cash Dividends Paid no está certificado como distribución FIBRA/REIT; se excluye del voto")
        elif period != "annual": warnings.append("Payout sobre FFO no disponible: la distribución no está identificada como anual; se evita mezclar períodos")
        if net_debt_to_ebitda is None: warnings.append("Net debt/EBITDA REIT no disponible: falta EBITDA o deuda neta válida")
        if interest_coverage is None: warnings.append("Cobertura de intereses REIT no disponible: falta EBITDA/interés válido")
        if required_yield-growth < .04: warnings.append("Valoración sensible: spread entre yield requerido y crecimiento < 4pp")
        if margin < 0: warnings.append("Precio de mercado supera el valor razonable del modelo FFO")
        return REITValuationResult(True,"FFO_CAPITALIZATION",ffo_per_share,fair_value,margin,score,required_yield,growth,source_quality,warnings,valuation_quality,affo_per_share,distribution_per_share,payout_ratio,period,distribution_source,nav_per_share,cap_rate,net_debt_to_ebitda,interest_coverage,components,len(components)/4.0)
