from investment_analyzer.analysis.decision.signal_builder import build_decision_inputs
from investment_analyzer.analysis.decision.decision_engine import DecisionEngine


def test_real_components_use_35_30_20_15_and_context_does_not_vote():
    strategic, tactical, contextual, confidence = build_decision_inputs(
        enriched={
            'fundamental_score': 80, 'valuation_score': 70,
            'technical_score': 60, 'risk_score': 50,
            'sentiment_score': 40, 'smart_money_score': 90,
            'peer_valuation_score': 10, 'interest_rate_score': 0,
        }, specialized={}, analysis={}
    )
    result = DecisionEngine().evaluate(
        strategic, tactical,
        {'provider_quality':100,'freshness':100,'consistency':100,'completeness':100,'technical_data_quality':100},
        contextual=contextual,
    )
    assert result.strategic_score == 69.5
    assert result.tactical_score == 61.5
    assert result.contextual['peer_valuation'] == 10
    assert result.contextual['interest_rate_context'] == 0


def test_missing_component_is_not_replaced_by_50():
    strategic, tactical, _, _ = build_decision_inputs(
        enriched={'fundamental_score':80,'valuation_score':70}, specialized={}, analysis={}
    )
    result = DecisionEngine().evaluate(strategic, tactical, {'provider_quality':100,'freshness':100,'consistency':100,'completeness':100})
    assert result.strategic_score == 75.0
    assert result.strategic_coverage == 50.0
    assert result.tactical_score is None
