"""V12.59 adaptive text report for all supported asset classes."""
from __future__ import annotations
from collections.abc import Mapping

class MultiAssetReport:
    def render(self, context, symbol=None)->str:
        md=getattr(context,'metadata',{}) or {}; cls=md.get('asset_classification',{}); kind=cls.get('asset_type','UNKNOWN'); symbol=symbol or getattr(getattr(context,'asset',None),'symbol','N/D'); a=md.get('specialized_analysis',{}); data=a.get('analysis',a) if isinstance(a,Mapping) else {}
        lines=['='*64,'V12 — INFORME DE DECISIÓN DE INVERSIÓN','='*64,f'Activo: {symbol}',f'Tipo: {kind}',f'Confianza clasificación: {cls.get("confidence","N/D")}%','']
        if 'strategic_score' in data: lines += [f'DECISIÓN ESTRATÉGICA  Score: {data["strategic_score"]}/100  Cobertura: {data.get("strategic_coverage","N/D")}%',f'DECISIÓN TÁCTICA      Score: {data.get("tactical_score","N/D")}/100  Cobertura: {data.get("tactical_coverage","N/D")}%','']
        s=data.get('strategic',data.get('components',{}).get('strategic',{})); t=data.get('tactical',data.get('components',{}).get('tactical',{}))
        if kind=='ETF': lines += ['ETF — COMPOSICIÓN Y COSTOS',f'Expense ratio: {data.get("expense_ratio","N/D")}']
        elif kind in ('REIT','FIBRA'): lines += ['REIT / FIBRA — VALORACIÓN ESPECÍFICA',f'FFO/share: {data.get("ffo_share","N/D")}',f'AFFO/share: {data.get("affo_share","N/D")}',f'NAV/share: {data.get("nav_share","N/D")}',f'Distribución/share: {data.get("distribution_share","N/D")}']
        elif kind=='CRYPTO': lines += ['CRYPTO — MÉTRICAS',f'Market cap: {data.get("market_cap","N/D")}',f'Volumen 24h: {data.get("volume_24h","N/D")}',f'Supply: {data.get("circulating_supply","N/D")}',f'Max drawdown: {data.get("max_drawdown","N/D")}']
        elif kind=='BOND': lines += ['BONO — VALORACIÓN',f'Fair value: {data.get("fair_price","N/D")}',f'Rate sensitivity: {data.get("rate_sensitivity","N/D")}']
        elif kind=='STOCK': lines += ['ACCIÓN — VALORACIÓN',f'Fair value: {data.get("fair_value","N/D")}',f'Margin of safety: {data.get("margin_of_safety","N/D")}%']
        lines += ['', 'CONTEXTO — NO VOTA DIRECTAMENTE',f'Comparables: {"Disponible" if getattr(context,"comparables",None) is not None else "N/D"}',f'Macro: {"Disponible" if getattr(context,"macro",None) is not None else "N/D"}']
        if data.get('warnings'): lines += ['', 'ADVERTENCIAS']+[f'- {w}' for w in data['warnings']]
        if cls.get('warnings'): lines += [f'- {w}' for w in cls['warnings']]
        return '\n'.join(lines)
