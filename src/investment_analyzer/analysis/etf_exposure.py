"""V12.62 ETF sector/country exposure aggregation."""
from __future__ import annotations
from collections import defaultdict
from typing import Any,Mapping

class ETFExposureAnalyzer:
    def analyze(self, holdings=None):
        sector=defaultdict(float); country=defaultdict(float)
        rows=holdings or []
        for h in rows:
            if not isinstance(h,Mapping): continue
            w=h.get('weight')
            try: w=float(w or 0); w=w*100 if 0<=w<=1 else w
            except (TypeError,ValueError): continue
            s=h.get('sector') or h.get('industry')
            c=h.get('country') or h.get('region')
            if s: sector[str(s)]+=w
            if c: country[str(c)]+=w
        return {'sector':sorted(sector.items(),key=lambda x:x[1],reverse=True),'country':sorted(country.items(),key=lambda x:x[1],reverse=True),'sector_top1':max(sector.values()) if sector else None,'country_top1':max(country.values()) if country else None}
