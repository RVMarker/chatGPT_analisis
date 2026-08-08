"""V12.11 deterministic JSON/CLI report for the V11 decision result."""
from __future__ import annotations
import json
from dataclasses import asdict, is_dataclass
from typing import Any

SCHEMA_VERSION="12.11"

def _plain(value: Any):
    if is_dataclass(value): return {k:_plain(v) for k,v in asdict(value).items()}
    if isinstance(value, dict): return {str(k):_plain(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [_plain(v) for v in value]
    return value

def decision_to_dict(result):
    data=_plain(result); data["schema_version"]=SCHEMA_VERSION
    data["decision_summary"]={"strategic":{"verdict":data.get("strategic_decision"),"score":data.get("strategic_score"),"coverage":data.get("strategic_coverage")},"tactical":{"verdict":data.get("tactical_decision"),"score":data.get("tactical_score"),"coverage":data.get("tactical_coverage")},"confidence":data.get("confidence"),"data_coverage":data.get("data_coverage")}
    return data

def render_cli(result)->str:
    d=decision_to_dict(result); s=d["decision_summary"]
    lines=["="*76,"V12.11 — INFORME DE DECISIÓN DE INVERSIÓN","="*76,f"DECISIÓN ESTRATÉGICA (años) : {s['strategic']['verdict']}",f"Score                     : {s['strategic']['score']}",f"Cobertura                 : {s['strategic']['coverage']}%","",f"DECISIÓN TÁCTICA (semanas) : {s['tactical']['verdict']}",f"Score                     : {s['tactical']['score']}",f"Cobertura                 : {s['tactical']['coverage']}%","",f"CALIDAD / CONFIANZA       : {d.get('confidence')}%",f"Cobertura decisoria       : {d.get('data_coverage')}%"]
    for horizon in ("strategic","tactical"):
        p=(d.get("actionable") or {}).get(horizon)
        if p: lines += ["",f"ACCIÓN {horizon.upper()}: {p.get('action')}",f"Robustez: {p.get('robustness')} | Severidad: {p.get('severity')}",f"Racional: {p.get('rationale')}"]
    if d.get("decisive_factors"): lines += ["","FACTORES DECISIVOS"]+[f"- {x}" for x in d["decisive_factors"]]
    if d.get("missing_factors"): lines += ["","DATOS FALTANTES / BLOQUEADOS"]+[f"- {x}" for x in d["missing_factors"]]
    return "\n".join(lines)

def render_json(result,*,indent=2)->str:
    return json.dumps(decision_to_dict(result),ensure_ascii=False,indent=indent,default=str)
