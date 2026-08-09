"""Regression tests for V12.75 specialized routing.
These tests use injected fake dependencies, so they do not require live market data.
"""
from investment_analyzer.pipeline.end_to_end import InvestmentPipeline


class FakeClassifier:
    def __init__(self, asset): self.asset=asset
    def classify(self, *args, **kwargs):
        class C:
            confidence=100
            def as_dict(self): return {'asset_type': self.asset,'confidence':100}
        c=C(); c.asset=self.asset; return c


class FakeIdentity:
    def normalize_asset_type(self, x): return x
    def register(self, **kwargs):
        class I:
            def as_dict(self): return kwargs
        return I()


class FakeRoute:
    required_fields=[]


class FakeRouter:
    def plan(self, asset, symbol): return {'required_fields': []}


class FakeAcq:
    enriched={}
    fields={}
    missing_required=[]
    def __init__(self, enriched): self.enriched=enriched
    def acquire(self, **kwargs): return self
    def as_dict(self): return {'enriched':self.enriched}


class FakeConsensus:
    def evaluate_batch(self, *args, **kwargs): return {}


def make(asset, enriched):
    p=InvestmentPipeline(classifier=FakeClassifier(asset), identity_registry=FakeIdentity(), router=FakeRouter(), acquisition=FakeAcq(enriched), consensus=FakeConsensus())
    return p.run(symbol='TEST', asset_type=asset, data_quality=100)


def test_crypto_routes_to_specialized_engine():
    r=make('CRYPTO', {'market_cap':1000000,'volume_24h':50000,'price':10})
    assert 'crypto' in r.specialized_analysis
    assert 'crypto_decision' in r.specialized_analysis


def test_bond_routes_to_specialized_engine():
    r=make('BOND', {'price':98,'face_value':100,'coupon_rate':.08,'ytm':.09,'years_to_maturity':5,'duration':4})
    assert 'bond' in r.specialized_analysis
    assert 'bond_decision' in r.specialized_analysis


def test_etf_routes_to_specialized_engine():
    r=make('ETF', {'price':100,'expense_ratio':.001,'holdings':[{'symbol':'A','weight':.1}]})
    assert 'etf' in r.specialized_analysis
