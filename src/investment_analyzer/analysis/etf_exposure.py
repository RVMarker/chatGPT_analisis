"""V12.64 ETF sector/country exposure and concentration analysis."""
from __future__ import annotations
from collections import defaultdict
from typing import Mapping

class ETFExposureAnalyzer:
    def analyze(self, holdings=None):
        sector=defaultdict(float); country=defaultdict(float); rows=holdings or []
        for h in rows:
            if not isinstance(h,Mapping): continue
            try:
                w=float(h.get('weight') or 0); w=w*100 if 0<=w<=1 else w
            except (TypeError,ValueError): continue
            for bucket,key1,key2 in ((sector,'sector','industry'),(country,'country','region')):
                value=h.get(key1) or h.get(key2)
                if value: bucket[str(value)]+=w
        sector_rows=sorted(sector.items(),key=lambda x:x[1],reverse=True); country_rows=sorted(country.items(),key=lambda x:x[1],reverse=True)
        return {'sector':sector_rows,'country':country_rows,'sector_top1':sector_rows[0][1] if sector_rows else None,'country_top1':country_rows[0][1] if country_rows else None,'sector_count':len(sector_rows),'country_count':len(country_rows),'sector_top3_weight':sum(x[1] for x in sector_rows[:3]),'country_top3_weight':sum(x[1] for x in country_rows[:3]),'coverage':{'sector_weight':sum(sector.values()),'country_weight':sum(country.values()),'holdings_count':len(rows)}}
