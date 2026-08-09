"""V12.47 normalize REIT/FIBRA cash-flow and balance-sheet fields."""
from __future__ import annotations
from typing import Any

class REITFibraEnricher:
    ALIASES={
        "price":("price","regularMarketPrice","last_price"),
        "ffo_share":("ffo_share","ffoPerShare","ffo_per_share","FFO_per_share"),
        "affo_share":("affo_share","affoPerShare","affo_per_share","AFFO_per_share"),
        "nav_share":("nav_share","navPerShare","nav_per_share","NAV_per_share"),
        "distribution_share":("distribution_share","distributionPerShare","dividendPerShare","distribution_per_share"),
        "payout_ffo":("payout_ffo","payoutFFO","ffo_payout","payoutRatio"),
        "net_debt_ebitda":("net_debt_ebitda","netDebtToEBITDA","net_debt_to_ebitda"),
        "interest_coverage":("interest_coverage","interestCoverage"),
        "cap_rate":("cap_rate","capRate"),
        "ffo_multiple":("ffo_multiple","ffoMultiple"),
        "affo_multiple":("affo_multiple","affoMultiple"),
        "required_return":("required_return","requiredReturn"),
    }
    def enrich(self,payloads:dict[str,dict[str,Any]])->dict[str,Any]:
        result={}; source_map={}; warnings=[]
        for field,keys in self.ALIASES.items():
            for provider,payload in (payloads or {}).items():
                for key in keys:
                    value=payload.get(key) if isinstance(payload,dict) else None
                    if value is not None:
                        result[field]=value; source_map[field]=provider; break
                if field in result: break
        for required in ("price","ffo_share"):
            if result.get(required) is None: warnings.append(f"{required} no disponible en proveedores consultados")
        result["source_map"]=source_map; result["warnings"]=warnings
        return result
