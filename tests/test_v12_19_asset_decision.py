from investment_analyzer.analysis.decision.asset_decision_engine import AssetDecisionEngine


def test_all_six_asset_classes_have_valid_weights():
    e=AssetDecisionEngine()
    for asset,cfg in e.WEIGHTS.items():
        assert abs(sum(cfg['strategic'].values())-1)<1e-9
        assert abs(sum(cfg['tactical'].values())-1)<1e-9
        assert e.normalize(asset)==asset


def test_missing_factor_is_not_neutralized_to_50():
    e=AssetDecisionEngine()
    r=e.evaluate('STOCK', {'fundamental':80,'valuation':None,'risk':40}, {'technical':60,'sentiment':None,'smart_money':40})
    assert r.strategic_coverage < 100
    assert r.tactical_coverage < 100
    assert r.strategic_score is not None
    assert all(x['score'] is not None for x in r.strategic_breakdown if x['available'])


def test_context_does_not_vote():
    e=AssetDecisionEngine()
    r=e.evaluate('ETF', {'quality':80,'valuation':80,'risk':80,'benchmark':80}, {'technical':60,'sentiment':60,'smart_money':60}, contextual={'macro':0,'comparables':100})
    assert r.strategic_score==80
    assert r.tactical_score==60
