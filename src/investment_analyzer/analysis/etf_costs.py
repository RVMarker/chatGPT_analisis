"""V12.65 ETF cost/efficiency metrics. Percentages are stored as percentage points."""
from __future__ import annotations
from typing import Any,Mapping

class ETFCostAnalyzer:
    def analyze(self,payload:Mapping[str,Any]|None=None)->dict[str,Any]:
        p=dict(payload or {})
        expense=self._num(p.get('expense_ratio',p.get('expenseRatio',p.get('annualReportExpenseRatio'))))
        if expense is not None and 0 < expense < 1: expense*=100
        benchmark_expense=self._num(p.get('category_median_expense_ratio',p.get('benchmark_expense_ratio')))
        if benchmark_expense is not None and 0 < benchmark_expense < 1: benchmark_expense*=100
        td=self._num(p.get('tracking_difference',p.get('trackingDifference')))
        te=self._num(p.get('tracking_error',p.get('trackingError')))
        y=self._num(p.get('yield',p.get('distribution_yield',p.get('dividend_yield'))))
        if y is not None and 0 < y < 1:y*=100
        result={'expense_ratio':expense,'benchmark_or_category_expense_ratio':benchmark_expense,'expense_premium_vs_category':None if expense is None or benchmark_expense is None else expense-benchmark_expense,'tracking_difference':td,'tracking_error':te,'yield':y,'cost_quality':None,'warnings':[]}
        if expense is None: result['warnings'].append('Expense ratio no disponible')
        else:
            score=100
            if benchmark_expense is not None: score-=max(0,(expense-benchmark_expense))*20
            if td is not None: score-=max(0,abs(td))*10
            result['cost_quality']=round(max(0,min(100,score)),2)
        return result
    @staticmethod
    def _num(v):
        try:return None if v is None else float(v)
        except (TypeError,ValueError):return None
