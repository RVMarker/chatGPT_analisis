"""REIT/FIBRA valuation engine V11.

Uses FFO/AFFO capitalization plus optional property/NAV and balance-sheet
quality metrics. P/E is intentionally not part of the REIT valuation score.
Every unavailable component remains N/D rather than being fabricated.
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
    valuation_quality: str = "MEDIUM"
    affo_per_share: float | None = None
    distribution_per_share: float | None = None
    payout_ratio: float | None = None
    distribution_period: str | None = None
    nav_per_share: float | None = None
    cap_rate: float | None = None
    net_debt_to_ebitda: float | None = None
    interest_coverage: float | None = None
    component_scores: dict[str, float] | None = None
    component_coverage: float = 0.0

    def as_dict(self):
        return asdict(self)


class REITValuationEngine:
    """Valuation model appropriate for REIT/FIBRA equity."""

    @staticmethod
    def _rate(name: str, value: float) -> float:
        value = float(value)
        if not 0.0 <= value < 1.0:
            raise ValueError(f"{name} debe estar entre 0 y 1")
        return value

    @staticmethod
    def _score(margin: float | None) -> float | None:
        if margin is None:
            return None
        if margin >= 0.30:
            return 100.0
        if margin >= 0.20:
            return 90.0
        if margin >= 0.10:
            return 80.0
        if margin >= 0.00:
            return 70.0
        if margin >= -0.10:
            return 55.0
        if margin >= -0.20:
            return 40.0
        if margin >= -0.30:
            return 25.0
        return 10.0

    @staticmethod
    def _quality(source_quality: str) -> str:
        quality = (source_quality or "").upper()
        if quality in {"FFO_OFFICIAL", "AFFO_OFFICIAL", "AFFO"}:
            return "HIGH"
        if quality in {"FFO_PROXY", "FFO_ESTIMATE"}:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _normalize_period(period: str | None) -> str | None:
        if period is None:
            return None
        normalized = str(period).strip().lower().replace("-", "_")
        aliases = {
            "annual": "annual", "year": "annual", "yearly": "annual",
            "fiscal_year": "annual", "fy": "annual",
            "quarter": "quarterly", "quarterly": "quarterly",
            "month": "monthly", "monthly": "monthly",
        }
        return aliases.get(normalized, normalized)

    @staticmethod
    def _leverage_score(net_debt_to_ebitda: float | None) -> float | None:
        if net_debt_to_ebitda is None:
            return None
        if net_debt_to_ebitda <= 2.0:
            return 100.0
        if net_debt_to_ebitda <= 3.0:
            return 85.0
        if net_debt_to_ebitda <= 4.0:
            return 70.0
        if net_debt_to_ebitda <= 5.0:
            return 50.0
        if net_debt_to_ebitda <= 6.0:
            return 30.0
        return 10.0

    @staticmethod
    def _coverage_score(interest_coverage: float | None) -> float | None:
        if interest_coverage is None:
            return None
        if interest_coverage >= 6:
            return 100.0
        if interest_coverage >= 4:
            return 85.0
        if interest_coverage >= 3:
            return 70.0
        if interest_coverage >= 2:
            return 50.0
        if interest_coverage >= 1:
            return 25.0
        return 10.0

    @staticmethod
    def _payout_score(payout_ratio: float | None) -> float | None:
        if payout_ratio is None:
            return None
        if payout_ratio <= 0.70:
            return 100.0
        if payout_ratio <= 0.85:
            return 90.0
        if payout_ratio <= 1.00:
            return 75.0
        if payout_ratio <= 1.10:
            return 50.0
        return 20.0

    def calculate(self, *, ffo: float, shares_outstanding: float, current_price: float,
                  required_yield: float = 0.09, growth: float = 0.03,
                  source_quality: str = "FFO_PROXY", affo: float | None = None,
                  distribution: float | None = None, distribution_period: str | None = None,
                  property_value: float | None = None, net_debt: float | None = None,
                  ebitda: float | None = None, interest_expense: float | None = None) -> REITValuationResult:
        required_yield = self._rate("required_yield", required_yield)
        growth = self._rate("growth", growth)
        valuation_quality = self._quality(source_quality)
        normalized_distribution_period = self._normalize_period(distribution_period)
        if required_yield <= growth:
            raise ValueError("required_yield debe ser mayor que growth")
        if shares_outstanding <= 0 or current_price <= 0:
            return REITValuationResult(False, "FFO_CAPITALIZATION", None, None, None, None,
                                       required_yield, growth, source_quality,
                                       ["Faltan acciones en circulación o precio actual válido"],
                                       valuation_quality, distribution_period=normalized_distribution_period)
        if ffo <= 0:
            return REITValuationResult(False, "FFO_CAPITALIZATION", None, None, None, None,
                                       required_yield, growth, source_quality,
                                       ["FFO no positivo; no se puede capitalizar de forma robusta"],
                                       valuation_quality, distribution_period=normalized_distribution_period)

        ffo_per_share = float(ffo) / float(shares_outstanding)
        fair_value = ffo_per_share * (1.0 + growth) / (required_yield - growth)
        margin = fair_value / float(current_price) - 1.0
        affo_per_share = float(affo) / float(shares_outstanding) if affo is not None else None
        distribution_per_share = None
        payout_ratio = None
        if distribution is not None and normalized_distribution_period == "annual":
            distribution_per_share = abs(float(distribution)) / float(shares_outstanding)
            payout_ratio = distribution_per_share / ffo_per_share if ffo_per_share > 0 else None
        nav_per_share = float(property_value) / float(shares_outstanding) if property_value is not None and property_value > 0 else None
        cap_rate = float(ffo) / float(property_value) if property_value is not None and property_value > 0 else None
        net_debt_to_ebitda = float(net_debt) / float(ebitda) if net_debt is not None and ebitda and ebitda > 0 else None
        interest_coverage = float(ebitda) / abs(float(interest_expense)) if ebitda and interest_expense and interest_expense != 0 else None

        component_scores: dict[str, float] = {}
        base_score = self._score(margin)
        if base_score is not None:
            component_scores["ffo_value"] = base_score
        payout_score = self._payout_score(payout_ratio)
        if payout_score is not None:
            component_scores["payout"] = payout_score
        leverage_score = self._leverage_score(net_debt_to_ebitda)
        if leverage_score is not None:
            component_scores["leverage"] = leverage_score
        coverage_score = self._coverage_score(interest_coverage)
        if coverage_score is not None:
            component_scores["interest_coverage"] = coverage_score

        reit_score = base_score
        if component_scores and len(component_scores) > 1:
            weights = {"ffo_value": 0.60, "payout": 0.15, "leverage": 0.15, "interest_coverage": 0.10}
            active = [(name, score, weights[name]) for name, score in component_scores.items()]
            total_weight = sum(weight for _, _, weight in active)
            reit_score = sum(score * weight for _, score, weight in active) / total_weight
        coverage = len(component_scores) / 4.0

        warnings: list[str] = []
        if source_quality == "FFO_PROXY":
            warnings.append("FFO PROXY: derivado de estados financieros; no sustituye AFFO/FFO oficial de la FIBRA")
        if valuation_quality != "HIGH":
            warnings.append(f"Calidad de valoración {valuation_quality}: el valor razonable depende de la calidad del FFO disponible")
        if affo is None:
            warnings.append("AFFO oficial no disponible; no se infiere AFFO a partir de FCF/capex")
        if property_value is None:
            warnings.append("NAV/cap-rate no disponibles: falta valor de propiedades validado")
        if distribution is None:
            warnings.append("Payout sobre FFO no disponible: falta distribución/dividendos trazables")
        elif normalized_distribution_period != "annual":
            warnings.append("Payout sobre FFO no disponible: la distribución no está identificada como anual; se evita mezclar períodos (trimestral/mensual/anual)")
        if net_debt_to_ebitda is None:
            warnings.append("Net debt/EBITDA REIT no disponible: falta EBITDA o deuda neta válida")
        if interest_coverage is None:
            warnings.append("Cobertura de intereses REIT no disponible: falta EBITDA/interés válido")
        if required_yield - growth < 0.04:
            warnings.append("Valoración sensible: spread entre yield requerido y crecimiento < 4pp")
        if margin < 0:
            warnings.append("Precio de mercado supera el valor razonable del modelo FFO")

        return REITValuationResult(
            True, "FFO_CAPITALIZATION", ffo_per_share, fair_value, margin, reit_score,
            required_yield, growth, source_quality, warnings, valuation_quality,
            affo_per_share, distribution_per_share, payout_ratio, normalized_distribution_period,
            nav_per_share, cap_rate, net_debt_to_ebitda, interest_coverage, component_scores, coverage,
        )
