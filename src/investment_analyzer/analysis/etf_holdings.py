"""V12.61 ETF composition, top holdings and cost analysis."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from typing import Any,Mapping

@dataclass(slots=True)
class ETFComposition:
    expense_ratio:float|None
    holdings:list[dict[str,Any]]
    top10_weight:float|None
    concentration_score:float|None
    warnings:list[str]
    def as_dict(self): return asdict(self)

class ETFCompositionAnalyzer:
    def analyze(self,*,holdings=None,expense_ratio=None)->ETFComposition:
        warnings=[]; rows=[]
        for item in holdings or []:
            if isinstance(item,Mapping):
                name=item.get('name') or item.get('symbol') or item.get('ticker') or 'N/D'; weight=item.get('weight')
            else:
                name=str(item); weight=None
            if weight is not None:
                try: weight=float(weight); weight=weight/100 if weight>1 else weight
                except (TypeError,ValueError): weight=None
            rows.append({'rank':len(rows)+1,'name':name,'weight':weight})
        rows.sort(key=lambda x:x['weight'] if x['weight'] is not None else -1,reverse=True)
        for i,r in enumerate(rows,1): r['rank']=i
        top=rows[:10]; top10=sum(r['weight'] for r in top if r['weight'] is not None) if top and any(r['weight'] is not None for r in top) else None
        score=None if top10 is None else max(0,min(100,100-top10*100))
        if expense_ratio is None: warnings.append('Expense ratio no disponible')
        if not rows: warnings.append('Composición del ETF no disponible')
        elif any(r['weight'] is None for r in top): warnings.append('Algunos pesos de holdings no están disponibles')
        return ETFComposition(expense_ratio,top,round(top10,6) if top10 is not None else None,round(score,2) if score is not None else None,warnings)
