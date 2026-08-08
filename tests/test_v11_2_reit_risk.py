from investment_analyzer.analysis.risk.risk_engine import RiskEngine
from investment_analyzer.common.models import BalanceSheet, CashFlow, FinancialStatements, IncomeStatement


def reit_statements():
    return FinancialStatements(
        balance=BalanceSheet(
            total_assets=10000, current_assets=1000, cash=500, inventory=0,
            receivables=300, total_liabilities=7000, current_liabilities=1000,
            long_term_debt=6000, shareholders_equity=3000, retained_earnings=1500,
            working_capital=0, property_value=9000,
        ),
        income=IncomeStatement(
            revenue=1000, gross_profit=800, operating_income=500, ebit=500,
            ebitda=700, pretax_income=300, net_income=250, eps=0.5,
            interest_expense=100,
        ),
        cashflow=CashFlow(operating_cash_flow=600, capex=-200, free_cash_flow=400),
        fiscal_date="2026-06-30",
    )


def test_reit_profile_does_not_vote_book_debt_equity_directly():
    result = RiskEngine().calculate(reit_statements(), market_value_equity=5000, is_reit=True)

    assert result.profile == "REIT_FIBRA"
    assert result.debt_to_equity == 7000 / 3000
    assert result.debt_to_ebitda == 6000 / 700
    assert result.market_leverage is not None
    assert result.metrics["debt_to_equity_role"] == "CONTEXT_ONLY"
    assert "ltv" in result.available_components


def test_corporate_profile_keeps_book_balance_component():
    result = RiskEngine().calculate(reit_statements(), market_value_equity=5000, is_reit=False)

    assert result.profile == "CORPORATE"
    assert "balance" in result.available_components
    assert "ltv" not in result.available_components
