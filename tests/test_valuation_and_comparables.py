from investment_analyzer.analysis.comparables.comparables_engine import ComparablesEngine
from investment_analyzer.analysis.valuation.valuation_engine import ValuationEngine


def test_valuation_engine_produces_normalized_score():
    result = ValuationEngine().from_dcf(
        100, [0.08, 0.07, 0.06, 0.05, 0.04], 0.10, 0.03,
        net_debt=100, shares_outstanding=10, current_price=50,
    )
    assert 0 <= result.score <= 100
    assert result.dcf is not None


def test_comparables_are_context_not_score():
    result = ComparablesEngine().calculate(
        pe=20, ev_ebitda=12, peer_pe=[10, 12, 14], peer_ev_ebitda=[8, 9, 10]
    )
    assert result.peer_pe_median == 12
    assert result.peer_ev_ebitda_median == 9
    assert result.pe_premium_discount > 0
    assert result.ev_ebitda_premium_discount > 0
