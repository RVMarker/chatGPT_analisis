"""Central provider registry with optional Yahoo adapter bridge."""
from __future__ import annotations
from typing import Any, Callable, Dict

class ProviderRegistry:
    def __init__(self, providers:dict[str,object]|None=None):
        self.providers: Dict[str, object] = {}
        for name, provider in (providers or {}).items(): self.register(name, provider)

    def register(self, name: str, provider) -> None:
        key=name.strip().lower()
        if not key: raise ValueError("provider name vacío")
        self.providers[key]=provider

    def get(self,name:str):
        key=name.strip().lower()
        if key not in self.providers: raise KeyError(f"Provider no registrado: {name}")
        return self.providers[key]

    def exists(self,name:str)->bool:return name.strip().lower() in self.providers
    def names(self):return sorted(self.providers)

    def register_defaults(self,yahoo_provider=None):
        if yahoo_provider is None:
            try:
                from investment_analyzer.providers.yahoo_adapter import YahooFinanceAdapter
                yahoo_provider=YahooFinanceAdapter()
            except Exception:
                yahoo_provider=None
        if yahoo_provider is not None:self.register("yahoo",yahoo_provider)
        return self

    @staticmethod
    def _model_to_payload(value:Any)->dict[str,Any]:
        if value is None:return {}
        if isinstance(value,dict):return value
        out={}
        if hasattr(value,"__dataclass_fields__"):
            for name in value.__dataclass_fields__:
                try: out[name]=getattr(value,name)
                except Exception: pass
        else:
            for name in dir(value):
                if name.startswith("_"):continue
                try:item=getattr(value,name)
                except Exception:continue
                if callable(item):continue
                if isinstance(item,(str,int,float,bool)) or item is None:out[name]=item
        return out

    def yahoo_fetcher(self,symbol:str):
        adapter=self.get("yahoo"); payload={}
        price=adapter.price(symbol)
        payload.update(self._model_to_payload(price))
        try:
            statements=adapter.financial_statements(symbol)
            for model in (statements.income,statements.balance,statements.cashflow): payload.update(self._model_to_payload(model))
            ffo=getattr(statements.cashflow,"ffo_proxy",None)
            if ffo is not None:payload["ffo"]=ffo
        except Exception:
            pass
        if not payload:raise RuntimeError(f"Yahoo no pudo obtener datos para {symbol}")
        return payload

    def fetchers(self)->dict[str,Callable[[str],Any]]:
        result={}
        if self.exists("yahoo"):result["yahoo"]=self.yahoo_fetcher
        for name,adapter in self.providers.items():
            if name=="yahoo":continue
            if callable(adapter):result[name]=adapter
            elif hasattr(adapter,"fetch"):result[name]=adapter.fetch
        return result
