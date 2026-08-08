"""V12.7 converts a verdict into an actionable but non-advisory policy label."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ActionPolicy:
    verdict: str
    severity: str
    robustness: str
    action: str
    rationale: str

class ActionPolicyEngine:
    def evaluate(self, verdict: str, score: float | None, confidence: float, coverage: float, red_flags=None) -> ActionPolicy:
        v=(verdict or "N/D").upper()
        if score is None or v == "N/D": return ActionPolicy(v,"N/D","BAJA","NO ACTUAR — DATOS INSUFICIENTES","No existe score decisorio utilizable")
        robustness="ALTA" if confidence>=80 and coverage>=80 else "MEDIA" if confidence>=60 and coverage>=60 else "BAJA"
        distance=abs(float(score)-50)
        severity="ALTA" if distance>=25 else "MODERADA" if distance>=10 else "BAJA"
        if robustness=="BAJA": action="NO AUMENTAR EXPOSICIÓN / REVISAR TESIS"
        elif v=="COMPRAR": action="CONSIDERAR ENTRADA GRADUAL"
        elif v=="ACUMULAR": action="CONSIDERAR ACUMULACIÓN GRADUAL"
        elif v=="MANTENER": action="MANTENER / MONITOREAR TESIS"
        elif v=="REDUCIR": action="REDUCIR EXPOSICIÓN GRADUALMENTE"
        elif v=="VENDER": action="CONSIDERAR REDUCCIÓN / SALIDA SEGÚN MANDATO"
        else: action="REVISAR TESIS"
        rationale=f"score={score:.1f}; confianza={confidence:.1f}%; cobertura={coverage:.1f}%"
        return ActionPolicy(v,severity,robustness,action,rationale)
