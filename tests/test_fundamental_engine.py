from investment_analyzer.analysis.fundamental.fundamental_engine import FundamentalEngine
from investment_analyzer.common.models import BalanceSheet, CashFlow, FinancialStatements, IncomeStatement


def statements():
    return FinancialStatements(
        balance=BalanceSheet(
            total_assets=1000, current_assets=400, cash=150, inventory=50,
            receivables=100, total_liabilities=400, current_liabilities=200,
            long_term_debt=200, shareholders_equity=600, retained_earnings=300,
        ),
        income=IncomeStatement(
            revenue=1000, gross_profit=400, operating_income=200, ebit=200,
            ebitda=250, pretax_income=180, net_income=150, eps=3,
            interest_expense=20,
        ),
        cashflow=CashFlow(
            operating_cash_flow=180, capex=-50, free_cash_flow=130,
            dividends_paid=-30, share_buybacks=-20,
        ),
        fiscal_date="2026-06-30",
    )


def test_fundamental_engine_returns_auditable_score():
    result = FundamentalEngine().calculate(statements())
    assert 0 <= result.score <= 100
    assert result.metrics["current_ratio"] == 2
    assert result.metrics["debt_to_equity"] == 400 / 600
    assert result.metrics["interest_coverage"] == 10
    assert result.metrics["fcf_margin"] == 0.13
    assert result.metrics["fiscal_date"] == "2026-06-30"
    assert result.strengths


def test_negative_cash_flow_is_a_red_flag():
    data = statements()
    data.cashflow.free_cash_flow = -20
    result = FundamentalEngine().calculate(data)
    assert "Flujo de caja libre negativo" in result.red_flags
