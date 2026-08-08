"""V12 REIT/FIBRA data-quality gate with cross-source validation."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Iterable
from investment_analyzer.providers.provenance import DataPoint, ProvenanceValidator

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
    validation_status: str | None = None
    source_count: int = 0
    spread_pct: float | None = None
    def as_dict(self): return asdict(self)

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
    cross_source: dict[str, dict[str, Any]] = field(default_factory=dict)
    overall_source_confidence: float = 0.0
    def as_dict(self):
        return {"asset_type":self.asset_type,"passed":self.passed,"coverage":self.coverage,"quality":self.quality,
                "evidence":{k:v.as_dict() for k,v in self.evidence.items()},"missing":list(self.missing),
                "warnings":list(self.warnings),"blocked_from_vote":list(self.blocked_from_vote),
                "cross_source":dict(self.cross_source),"overall_source_confidence":self.overall_source_confidence}

class REITDataQualityGate:
    REQUIRED=("ffo","affo","distribution","net_debt","ebitda","interest_expense","property_value","shares_outstanding")
    @staticmethod
    def _quality(value,source,verified,explicit_quality=None):
        if explicit_quality:return str(explicit_quality).upper()
        if value is None:return "MISSING"
        if verified and source:return "HIGH"
        if source:return "MEDIUM"
        return "LOW"
    @staticmethod
    def _role(field):
        if field in {"ffo","affo","distribution","net_debt","ebitda","interest_expense","property_value","shares_outstanding"}:
            return "VOTE" if field not in {"affo","distribution","property_value"} else "VOTE_IF_VERIFIED"
        return "CONTEXT"
    def validate(self,data:Mapping[str,Any],*,asset_type="FIBRA",source=None,fiscal_date=None,verified_fields=None,
                 field_sources=None,field_periods=None,field_quality=None,provider_points:Iterable[DataPoint]|None=None)->GateResult:
        asset=str(asset_type or "").upper(); verified_fields=set(verified_fields or ()); field_sources=dict(field_sources or {})
        field_periods=dict(field_periods or {}); field_quality=dict(field_quality or {}); evidence={}; missing=[]; warnings=[]; blocked=[]
        now=datetime.now(timezone.utc).isoformat(); points=tuple(provider_points or ())
        validation=ProvenanceValidator().validate_many(points,self.REQUIRED) if points else {}
        for field in self.REQUIRED:
            value=data.get(field); field_source=field_sources.get(field,source); verified=field in verified_fields
            vr=validation.get(field); quality=self._quality(value,field_source,verified,field_quality.get(field)); role=self._role(field); notes=""
            if vr and vr.status=="CONFLICT":
                blocked.append(field); warnings.append(f"{field}: CONFLICTO MATERIAL ENTRE FUENTES; excluido del voto hasta resolver"); quality="CONFLICT"
            elif vr and vr.status=="CONSISTENT" and quality in {"MEDIUM","LOW"}: quality="HIGH"
            if value is None:
                missing.append(field); blocked.append(field); notes="Dato ausente; no puede votar."
            elif quality in {"MISSING","LOW","UNKNOWN"} and role=="VOTE_IF_VERIFIED":
                blocked.append(field); warnings.append(f"{field}: evidencia no suficientemente verificada; excluido del voto específico")
            elif quality=="LOW" and field in {"ffo","net_debt","ebitda","interest_expense"}:
                warnings.append(f"{field}: fuente sin verificación explícita; se conserva pero reduce confianza")
            evidence[field]=Provenance(field,value,field_source,quality,field_periods.get(field,fiscal_date),now,verified,role,notes,
                                        vr.status if vr else None,len(vr.sources) if vr else (1 if value is not None else 0),vr.spread_pct if vr else None)
        if "debt_equity" in data and data.get("debt_equity") is not None:
            evidence["debt_equity"]=Provenance("debt_equity",data["debt_equity"],field_sources.get("debt_equity",source),field_quality.get("debt_equity","MEDIUM"),field_periods.get("debt_equity",fiscal_date),now,"debt_equity" in verified_fields,"CONTEXT","Para FIBRA: contexto contable; no sustituye LTV ni Net Debt/EBITDA.")
        available=sum(v.value is not None and v.quality!="CONFLICT" for v in evidence.values()); coverage=round(100*available/len(self.REQUIRED),2)
        if not data.get("ffo"):warnings.append("FFO no disponible: valoración REIT bloqueada")
        if data.get("ffo") is not None and not data.get("affo"):warnings.append("AFFO no disponible: no se infiere desde FCF/capex")
        if data.get("property_value") is None:warnings.append("NAV/cap rate bloqueados: falta valor de propiedades validado")
        if data.get("distribution") is None:warnings.append("Payout bloqueado: falta distribución verificable")
        cross={k:v.as_dict() for k,v in validation.items()}; source_conf=ProvenanceValidator.overall_confidence(validation) if validation else 0.0
        quality="HIGH" if coverage>=90 and not blocked and source_conf>=85 else "MEDIUM" if coverage>=60 else "LOW"
        passed=asset in {"FIBRA","REIT"} and data.get("ffo") is not None and data.get("shares_outstanding") is not None and not any(evidence[x].quality=="CONFLICT" for x in ("ffo","shares_outstanding"))
        return GateResult(asset,passed,coverage,quality,evidence,missing,list(dict.fromkeys(warnings)),list(dict.fromkeys(blocked)),cross,source_conf)
