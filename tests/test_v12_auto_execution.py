import pytest

from investment_analyzer.analysis.decision.trade_plan import build_trade_plan
from investment_analyzer.analysis.integration.fundamental_valuation_risk import FinancialAnalysisIntegrator
from investment_analyzer.common.models import BalanceSheet, CashFlow, FinancialStatements, IncomeStatement, PriceData


def _statements(*, fcf=100.0, historical_fcf=None, interest=5.0):
    return FinancialStatements(
        balance=BalanceSheet(
            total_assets=1000.0,
            current_assets=250.0,
            cash=20.0,
            total_liabilities=300.0,
            current_liabilities=150.0,
            long_term_debt=100.0,
            shareholders_equity=700.0,
            retained_earnings=500.0,
            working_capital=100.0,
        ),
        income=IncomeStatement(
            revenue=500.0,
            operating_income=120.0,
            ebit=120.0,
            ebitda=150.0,
            pretax_income=100.0,
            net_income=79.0,
            interest_expense=interest,
        ),
        cashflow=CashFlow(
            free_cash_flow=fcf,
            operating_cash_flow=130.0,
            capex=-30.0,
            historical_fcf=historical_fcf or [120.0, 110.0, 100.0],
        ),
        fiscal_date="2026-01-01",
    )


def _price(*, beta=1.1):
    return PriceData(
        symbol="TEST",
        current=100.0,
        market_cap=900.0,
        shares_outstanding=9.0,
        beta=beta,
    )


def test_growth_rates_are_derived_from_real_positive_fcf_history():
    rates, warnings = FinancialAnalysisIntegrator._growth_rates([100.0, 121.0, 144.0])
    assert rates is not None
    assert len(rates) == 5
    assert rates[0] == pytest.approx(0.2)
    assert rates[-1] < rates[0]
    assert warnings == []


def test_growth_forecast_does_not_create_extreme_negative_growth_from_old_history():
    rates, _ = FinancialAnalysisIntegrator._growth_rates([100.0, 108.0, 104.0, 102.0, 98.0])
    assert rates is not None
    assert rates[0] >= -0.02
    assert rates[-1] > -0.03


def test_terminal_growth_is_long_run_default_not_last_fcf_growth():
    result = FinancialAnalysisIntegrator().run(
        _statements(historical_fcf=[120.0, 110.0, 100.0]),
        _price(),
    )
    assert result.valuation["terminal_growth"] == pytest.approx(0.025)
    assert result.valuation["wacc_details"]["terminal_growth_method"] == "long_run_nominal_growth_default"


def test_fcff_conversion_adds_back_after_tax_interest_before_wacc_dcf():
    result = FinancialAnalysisIntegrator().run(
        _statements(fcf=100.0, historical_fcf=[90.0, 100.0], interest=10.0),
        _price(beta=1.0),
    )
    assert result.valuation["model"] == "FCFF_DCF"
    assert result.valuation["fcf_base_reported"] == pytest.approx(100.0)
    assert result.valuation["fcff_base"] == pytest.approx(108.0)
    assert result.valuation["fcff_conversion"]["method"] == "reported_FCF_plus_after_tax_interest"


def test_trade_plan_blocks_without_real_target1_resistance():
    plan = build_trade_plan(price=100.0, fair_value=140.0, bull_value=160.0, support=90.0, resistance=None, capital=5000.0, risk_pct=0.02, max_position_pct=0.25)
    assert plan["stop_loss"] == 90.0
    assert plan["target_1"] is None
    assert plan["target_2"] == 140.0
    assert plan["operation"] == "ESPERAR"
    assert "Target 1 no disponible" in plan["reasons"]


def test_trade_plan_uses_real_resistance_and_sizes_by_risk():
    plan = build_trade_plan(price=100.0, fair_value=140.0, bull_value=160.0, support=90.0, resistance=115.0, capital=5000.0, risk_pct=0.02, max_position_pct=0.25)
    assert plan["stop_loss"] == 90.0
    assert plan["target_1"] == 115.0
    assert plan["target_1_method"] == "20_period_resistance"
    assert plan["target_2"] == 140.0
    assert plan["risk_reward"] == pytest.approx(4.0)
    assert plan["units"] == 10
    assert plan["actual_risk"] == 100.0


def test_wacc_is_explicitly_derived_from_market_inputs():
    wacc, details = FinancialAnalysisIntegrator._derive_wacc(_statements(), _price(),)
    assert 0.06 <= wacc <= 0.18
    assert details["method"] == "CAPM_WACC"
    assert details["beta"] == pytest.approx(1.1)
    assert details["equity_weight"] == pytest.approx(0.9)
