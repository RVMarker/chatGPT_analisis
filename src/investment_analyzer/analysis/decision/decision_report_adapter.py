"""V12.20 adapter: normalize asset-specific decisions into the V11 report contract."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

ASSET_LABELS={"STOCK":"ACCION","ETF":"ETF","REIT":"REIT","FIBRA":"FIBRA","CRYPTO":"CRYPTO","BOND":"BONO"}

@dataclass(slots=True)
class DecisionReport:
    asset:str; strategic:dict[str,Any]; tactical:dict[str,Any]; quality:dict[str,Any]; breakdown_strategic:list[dict[str,Any]]; breakdown_tactical:list[dict[str,Any]]; context:dict[str,Any]; warnings:list[str]
    def as_dict(self): return asdict(self)

class DecisionReportAdapter:
    """Keeps context out of voting and preserves coverage-aware scores."""
    def build(self, *, asset_type:str, strategic:dict[str,Any], tactical:dict[str,Any], data_quality_score:float=100.0, context:dict[str,Any]|None=None, warnings:list[str]|None=None):
        asset=str(asset_type).upper(); strategic=self._normalize(strategic); tactical=self._normalize(tactical); quality=min(100.0,max(0.0,float(data_quality_score)))
        return DecisionReport(ASSET_LABELS.get(asset,asset),strategic,tactical,{"data_quality_pct":round(quality,1),"decision_coverage_pct":round((strategic["coverage_pct"]+tactical["coverage_pct"])/2,1),"decision_confidence_pct":round(quality*min(strategic["coverage_pct"],tactical["coverage_pct"])/100,1)},strategic["breakdown"],tactical["breakdown"],context or {},warnings or [])
    @staticmethod
    def _normalize(d:dict[str,Any]):
        score=d.get("score"); coverage=float(d.get("coverage_pct",d.get("coverage",0) or 0)); verdict=str(d.get("verdict","N/D")); breakdown=[]
        for item in d.get("breakdown",[]):
            score_i=float(item.get("score",0)); weight=float(item.get("weight_pct",item.get("weight",0))); contribution=score_i*weight/100
            breakdown.append({"factor":item.get("factor",item.get("name","unknown")),"score":round(score_i,2),"weight_pct":round(weight,2),"contribution":round(contribution,2),"contribution_pct":round(contribution,2)})
        return {"verdict":verdict,"score":None if score is None else round(float(score),2),"coverage_pct":round(max(0,min(100,coverage)),1),"breakdown":breakdown}
    @staticmethod
    def render_text(report:DecisionReport)->str:
        s=report.strategic; t=report.tactical; q=report.quality
        lines=["V12.20 — INFORME DE DECISIÓN DE INVERSIÓN",f"Activo: {report.asset}","","DECISIÓN ESTRATÉGICA (años)",f"Veredicto : {s['verdict']}",f"Score     : {s['score'] if s['score'] is not None else 'N/D'}/100",f"Cobertura : {s['coverage_pct']:.1f}%","","DECISIÓN TÁCTICA (semanas)",f"Veredicto : {t['verdict']}",f"Score     : {t['score'] if t['score'] is not None else 'N/D'}/100",f"Cobertura : {t['coverage_pct']:.1f}%","","CALIDAD / CONFIANZA",f"Calidad de datos base : {q['data_quality_pct']:.1f}%",f"Cobertura decisoria   : {q['decision_coverage_pct']:.1f}%",f"Confianza de decisión : {q['decision_confidence_pct']:.1f}%"]
        for title,items in (("DESGLOSE ESTRATÉGICO",s["breakdown"]),("DESGLOSE TÁCTICO",t["breakdown"])):
            lines += ["",title]+[f"{x['factor']:<16} score={x['score']:6.2f} peso={x['weight_pct']:5.1f}% aporte={x['contribution']:6.2f} aporte%={x['contribution_pct']:5.1f}" for x in items]
        if report.context: lines += ["","CONTEXTO — NO VOTA DIRECTAMENTE",str(report.context)]
        if report.warnings: lines += ["","ADVERTENCIAS"]+list(dict.fromkeys(report.warnings))
        return "\n".join(lines)
