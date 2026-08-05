import pytest

from investment_analyzer.analysis.valuation.dcf_engine import DCFEngine


def test_dcf_returns_fair_value_and_margin():
    result = DCFEngine().calculate(
        fcf_base=100,
        growth_rates=[0.10, 0.08, 0.06, 0.05, 0.04],
        wacc=0.10,
        terminal_growth=0.03,
        net_debt=100,
        shares_outstanding=10,
        current_price=80,
    )
    assert result.enterprise_value > 0
    assert result.equity_value > 0
    assert result.fair_value_per_share > 0
    assert result.margin_of_safety is not None


def test_dcf_rejects_terminal_growth_at_or_above_wacc():
    with pytest.raises(ValueError):
        DCFEngine().calculate(100, [0.05, 0.04], 0.08, 0.08)


def test_sensitivity_has_one_row_per_combination():
    rows = DCFEngine().sensitivity(100, [0.05, 0.04], [0.08, 0.10], [0.02, 0.03])
    assert len(rows) == 4
    assert all("fair_value_per_share" in row for row in rows)
