"""V12.82 report regression: final report must expose the decision engine's weights."""
from types import SimpleNamespace
from investment_analyzer.pipeline.decision_report import render_decision_report


def _component(name, score, weight, available=True):
    return SimpleNamespace(name=name, score=score, weight=weight,
                           weighted=score*weight, contribution_pct=score*weight,
                           available=available)


def test_report_displays_weighted_strategic_and_tactical_breakdown():
    decision = SimpleNamespace(
        strategic_decision='COMPRAR', tactical_decision='MANTENER',
        strategic_score=75.15, tactical_score=70.0,
        strategic_sufficient=True, tactical_sufficient=True,
        strategic_coverage=100.0, tactical_coverage=100.0,
        confidence=91.0, data_coverage=100.0, base_confidence=95.0,
        strategic_breakdown=[
            _component('fundamental',82,.35), _component('valuation',74,.30),
            _component('technical',68,.20), _component('risk',71,.15)],
        tactical_breakdown=[
            _component('technical',68,.45), _component('sentiment',72,.30),
            _component('smart_money',81,.25)],
        contextual={'comparables':80.0,'macro':70.0}, strengths=[], red_flags=[])
    context=SimpleNamespace(
        decision=decision,
        asset=SimpleNamespace(symbol='TEST'), metadata={},
        valuation={}, risk={}, comparables={}, macro={})
    text=render_decision_report(context)
    assert 'fundamental' in text and '35.0%' in text
    assert 'valuation' in text and '30.0%' in text
    assert 'technical' in text and '45.0%' in text
    assert 'sentiment' in text and '30.0%' in text
    assert 'smart_money' in text and '25.0%' in text
    assert 'CONTEXTO — NO VOTA DIRECTAMENTE' in text
