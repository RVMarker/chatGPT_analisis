"""V11.8 data-quality and provenance gate for REIT/FIBRA analysis.

The gate validates evidence before it is allowed to influence valuation or
risk. It never manufactures missing REIT metrics. Missing/ambiguous values
remain N/D and are reported as confidence limitations.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(slots=True)
class Provenance:
    field: str
    value: Any
    source: str | None = None
    quality: str = "UNKNOWN"
    period: str | None = None
    as_of: str | None = None
    verified: bool = False
    role: str = "CONTEXT"
    notes: str = ""

    def as_dict(self):
        return asdict(self)


@dataclass(slots=True)
class GateResult:
    asset_type: str
    passed: bool
    coverage: float
    quality: str
    evidence: dict[str, Provenance] = field(default_factory=dict)
    missing: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    blocked_from_vote: list[str] = field(default_factory=list)

    def as_dict(self):
        return {
            "asset_type": self.asset_type,
            "passed": self.passed,
            "coverage": self.coverage,
            "quality": self.quality,
            "evidence": {k: v.as_dict() for k, v in self.evidence.items()},
            "missing": list(self.missing),
            "warnings": list(self.warnings),
            "blocked_from_vote": list(self.blocked_from_vote),
        }


class REITDataQualityGate:
    REQUIRED = (
        "ffo",
        "affo",
        "distribution",
        "net_debt",
        "ebitda",
        "interest_expense",
        "property_value",
        "shares_outstanding",
    )

    @staticmethod
    def _quality(value, source, verified, explicit_quality=None):
        if explicit_quality:
            return str(explicit_quality).upper()
        if value is None:
            return "MISSING"
        if verified and source:
            return "HIGH"
        if source:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _role(field):
        if field in {"ffo", "affo", "distribution", "net_debt", "ebitda", "interest_expense", "property_value", "shares_outstanding"}:
            return "VOTE" if field not in {"affo", "distribution", "property_value"} else "VOTE_IF_VERIFIED"
        return "CONTEXT"

    def validate(self, data: Mapping[str, Any], *, asset_type="FIBRA", source=None,
                 fiscal_date=None, verified_fields=None, field_sources=None,
                 field_periods=None, field_quality=None) -> GateResult:
        asset = str(asset_type or "").upper()
        verified_fields = set(verified_fields or ())
        field_sources = dict(field_sources or {})
        field_periods = dict(field_periods or {})
        field_quality = dict(field_quality or {})
        evidence = {}
        missing = []
        warnings = []
        blocked = []
        now = datetime.now(timezone.utc).isoformat()

        for field in self.REQUIRED:
            value = data.get(field)
            field_source = field_sources.get(field, source)
            verified = field in verified_fields
            quality = self._quality(value, field_source, verified, field_quality.get(field))
            role = self._role(field)
            notes = ""
            if value is None:
                missing.append(field)
                blocked.append(field)
                notes = "Dato ausente; no puede votar."
            elif quality in {"MISSING", "LOW", "UNKNOWN"} and role == "VOTE_IF_VERIFIED":
                blocked.append(field)
                warnings.append(f"{field}: evidencia no suficientemente verificada; excluido del voto específico")
            elif quality == "LOW" and field in {"ffo", "net_debt", "ebitda", "interest_expense"}:
                warnings.append(f"{field}: fuente sin verificación explícita; se conserva pero reduce confianza")
            evidence[field] = Provenance(
                field=field,
                value=value,
                source=field_source,
                quality=quality,
                period=field_periods.get(field, fiscal_date),
                as_of=now,
                verified=verified,
                role=role,
                notes=notes,
            )

        # D/E is deliberately contextual for FIBRA. Do not let an accounting
        # ratio with ambiguous equity dominate REIT risk.
        if "debt_equity" in data and data.get("debt_equity") is not None:
            evidence["debt_equity"] = Provenance(
                field="debt_equity", value=data["debt_equity"], source=field_sources.get("debt_equity", source),
                quality=field_quality.get("debt_equity", "MEDIUM"), period=field_periods.get("debt_equity", fiscal_date),
                as_of=now, verified="debt_equity" in verified_fields, role="CONTEXT",
                notes="Para FIBRA: contexto contable; no sustituye LTV ni Net Debt/EBITDA."
            )

        available = sum(v.value is not None for v in evidence.values())
        coverage = round(100.0 * available / len(self.REQUIRED), 2)
        if not data.get("ffo"):
            warnings.append("FFO no disponible: valoración REIT bloqueada")
        if data.get("ffo") is not None and not data.get("affo"):
            warnings.append("AFFO no disponible: no se infiere desde FCF/capex")
        if data.get("property_value") is None:
            warnings.append("NAV/cap rate bloqueados: falta valor de propiedades validado")
        if data.get("distribution") is None:
            warnings.append("Payout bloqueado: falta distribución verificable")
        quality = "HIGH" if coverage >= 90 and not blocked else "MEDIUM" if coverage >= 60 else "LOW"
        passed = asset in {"FIBRA", "REIT"} and data.get("ffo") is not None and data.get("shares_outstanding") is not None
        return GateResult(asset, passed, coverage, quality, evidence, missing, list(dict.fromkeys(warnings)), list(dict.fromkeys(blocked)))
