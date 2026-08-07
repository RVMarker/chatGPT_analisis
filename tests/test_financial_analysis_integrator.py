from investment_analyzer.analysis.integration import FinancialAnalysisIntegrator
from investment_analyzer.common.models import BalanceSheet, CashFlow, FinancialStatements, IncomeStatement, PriceData


def snapshot():
    statements = FinancialStatements(
        balance=BalanceSheet(total_assets=1000, current_assets=400, cash=150, total_liabilities=400,
                             current_liabilities=200, long_term_debt=200, shareholders_equity=600,
                             retained_earnings=300),
        income=IncomeStatement(revenue=1000, operating_income=200, ebit=200, ebitda=250,
                               net_income=150, interest_expense=20),
        cashflow=CashFlow(operating_cash_flow=180, capex=-50, free_cash_flow=130),
        fiscal_date="2026-06-30",
    )
    price = PriceData(symbol="FMTY14.MX", current=80, market_cap=800, shares_outstanding=10)
    return statements, price


def test_integrator_runs_real_engines_together():
    statements, price = snapshot()
    result = FinancialAnalysisIntegrator().run(
        statements, price, growth_rates=[.10, .08, .06, .05, .04],
        wacc=.10, terminal_growth=.03,
    )
    assert 0 <= result.fundamental["score"] <= 100
    assert result.valuation["fair_value_per_share"] > 0
    assert 0 <= result.risk["score"] <= 100
    assert result.fundamental["metrics"]["current_ratio"] == 2


def test_integrator_marks_missing_fcf_as_unavailable():
    statements, price = snapshot()
    statements.cashflow.free_cash_flow = None
    result = FinancialAnalysisIntegrator().run(
        statements, price, growth_rates=[.05], wacc=.10, terminal_growth=.03
    )
    assert result.valuation["available"] is False
    assert result.valuation["score"] is None
    assert any("free_cash_flow" in warning for warning in result.valuation["warnings"])
