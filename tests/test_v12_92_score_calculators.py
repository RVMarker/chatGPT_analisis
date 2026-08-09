from investment_analyzer.analysis.decision.score_calculators import fundamental_score, valuation_score, technical_score, risk_score


def test_fundamental_score_from_raw_metrics():
    s=fundamental_score({'roe':20,'roic':15,'revenue_growth':20,'eps_growth':20,'fcf_margin':25,'debt_to_equity':0,'current_ratio':2})
    assert s == 100


def test_valuation_score_from_raw_metrics():
    s=valuation_score({'pe':10,'ev_ebitda':8,'margin_of_safety':40,'fcf_yield':10,'peg':0})
    assert s == 100


def test_missing_metrics_do_not_become_neutral_50():
    assert fundamental_score({'roe':20}) == 100
    assert valuation_score({}) is None
    assert technical_score({}) is None
    assert risk_score({}) is None
