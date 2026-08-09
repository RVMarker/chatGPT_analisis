from types import SimpleNamespace

import pytest

from investment_analyzer.analysis.decision.trade_plan import build_trade_plan
from investment_analyzer.analysis.integration.fundamental_valuation_risk import FinancialAnalysisIntegrator


def test_growth_rates_are_derived_from_real_positive_fcf_history():
    rates, warnings = FinancialAnalysisIntegrator._growth_rates([100.0, 121.0, 144.0])
    assert rates is not None
    assert len(rates) == 5
    assert rates[0] == pytest.approx(0.2)
    assert rates[-1] < rates[0]
    assert warnings == []


def test_trade_plan_creates_target_one_from_one_r_when_resistance_is_missing():
    plan = build_trade_plan(
        price=100.0,
        fair_value=140.0,
        bull_value=160.0,
        support=90.0,
        resistance=None,
        capital=5000.0,
        risk_pct=0.02,
        max_position_pct=0.25,
    )
    assert plan["stop_loss"] == 90.0
    assert plan["target_1"] == 110.0
    assert plan["target_1_method"] == "1R"
    assert plan["target_2"] == 140.0
    assert plan["risk_reward"] == pytest.approx(4.0)
    assert plan["units"] == 10
    assert plan["actual_risk"] == 100.0


def test_wacc_is_explicitly_derived_from_market_inputs():
    statements = SimpleNamespace(
        balance=SimpleNamespace(long_term_debt=100.0),
        income=SimpleNamespace(interest_expense=5.0, pretax_income=100.0, net_income=79.0),
    )
    price = SimpleNamespace(beta=1.1, market_cap=900.0)
    wacc, details = FinancialAnalysisIntegrator._derive_wacc(statements, price)
    assert 0.06 <= wacc <= 0.18
    assert details["method"] == "CAPM_WACC"
    assert details["beta"] == pytest.approx(1.1)
    assert details["equity_weight"] == pytest.approx(0.9)
