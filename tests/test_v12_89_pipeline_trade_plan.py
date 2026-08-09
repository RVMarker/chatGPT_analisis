"""V12.89 regression tests for the integrated operational decision path."""
from investment_analyzer.pipeline.end_to_end import InvestmentPipeline


def test_pipeline_builds_trade_plan_and_position_sizing(monkeypatch):
    pipeline = InvestmentPipeline()
    pipeline.classifier.classify = lambda *a, **k: type('C', (), {
        'asset_type':'STOCK','confidence':100,
        'as_dict':lambda self:{'asset_type':'STOCK','confidence':100}
    })()
    pipeline.router.plan = lambda *a, **k: {'required_fields':[], 'optional_fields':[]}
    pipeline.identity.register = lambda **k: type('I', (), {
        'as_dict':lambda self:{'symbol':k['symbol'],'canonical_id':'TEST'}
    })()
    pipeline.acquisition.acquire = lambda **k: type('A', (), {
        'enriched': {'price':100,'fair_value':130,'technical_support':92,'technical_resistance':115},
        'fields':{}, 'missing_required':[],
        'as_dict':lambda self:{'enriched':self.enriched,'fields':self.fields}
    })()
    pipeline.consensus.evaluate_batch = lambda *a, **k: {}
    result = pipeline.run(symbol='TEST',capital=5000,risk_pct=.02,max_position_pct=.25)
    payload=result.as_dict()
    assert payload['decision']['trade_plan']['stop_loss']==92
    assert payload['decision']['trade_plan']['target_1']==115
    assert payload['decision']['trade_plan']['target_2']==130
    assert payload['decision']['quality_gate']['operation'] in {'COMPRAR','ESPERAR','VENDER'}
