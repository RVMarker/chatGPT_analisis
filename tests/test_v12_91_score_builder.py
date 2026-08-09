from investment_analyzer.analysis.decision.score_builder import build_scores

class C: pass

def test_build_scores_reads_real_analysis_outputs():
    c=C(); c.fundamentals={'fundamental_score':82}; c.valuation={'dcf_score':74}; c.technical={'technical_score':68}; c.risk={'risk_score':71}; c.sentiment={'sentiment_score':63}; c.comparables={'peer_valuation_score':55}; c.macro={'interest_rate_score':30}; c.metadata={'smart_money':{'smart_money_score':81}}
    s=build_scores(c)
    assert s['strategic']=={'fundamental':82.0,'valuation':74.0,'technical':68.0,'risk':71.0}
    assert s['tactical']=={'technical':68.0,'sentiment':63.0,'smart_money':81.0}
    assert s['contextual']=={'comparables':55.0,'macro':30.0}

def test_missing_scores_remain_missing():
    c=C(); c.fundamentals={'fundamental_score':82}; c.valuation={}; c.technical={'available':False}; c.risk={}; c.sentiment={}; c.comparables={}; c.macro={}; c.metadata={}
    s=build_scores(c)
    assert s['strategic']['fundamental']==82.0
    assert s['strategic']['valuation'] is None
    assert s['strategic']['technical'] is None
    assert s['strategic']['risk'] is None
