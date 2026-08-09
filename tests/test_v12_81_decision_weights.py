from investment_analyzer.analysis.decision.decision_engine import DecisionEngine
from investment_analyzer.analysis.decision.decision_weights import STRATEGIC, TACTICAL


def test_strategic_weights_are_35_30_20_15():
    assert STRATEGIC == {'fundamental': .35, 'valuation': .30, 'technical': .20, 'risk': .15}
    assert sum(STRATEGIC.values()) == 1.0


def test_macro_and_comparables_do_not_vote():
    engine=DecisionEngine()
    base=engine.evaluate(
        {'fundamental':80,'valuation':80,'technical':80,'risk':80},
        {'technical':80,'sentiment':80,'smart_money':80},
        {}, contextual={'comparables':0,'macro':100,'peer_valuation':100,'interest_rate_context':0})
    changed=engine.evaluate(
        {'fundamental':80,'valuation':80,'technical':80,'risk':80},
        {'technical':80,'sentiment':80,'smart_money':80},
        {}, contextual={'comparables':100,'macro':0,'peer_valuation':0,'interest_rate_context':100})
    assert base.strategic_score == changed.strategic_score
    assert base.tactical_score == changed.tactical_score
    assert 'comparables' in base.contextual
    assert 'macro' in base.contextual


def test_missing_strategic_factor_is_excluded_and_coverage_reported():
    result=DecisionEngine().evaluate(
        {'fundamental':80,'valuation':80,'technical':None,'risk':80},
        {'technical':80,'sentiment':80,'smart_money':80}, {}, {})
    assert result.strategic_coverage == 75.0
    assert result.strategic_score == 80.0
