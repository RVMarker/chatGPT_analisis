from investment_analyzer.analysis.risk.risk_engine import RiskEngine
from investment_analyzer.common.models import BalanceSheet, CashFlow, FinancialStatements, IncomeStatement


def statements():
    return FinancialStatements(
        balance=BalanceSheet(
            total_assets=1000, current_assets=400, cash=150, inventory=50,
            receivables=100, total_liabilities=300, current_liabilities=150,
            long_term_debt=150, shareholders_equity=700, retained_earnings=400,
            working_capital=250,
        ),
        income=IncomeStatement(
            revenue=1000, gross_profit=400, operating_income=200, ebit=200,
            ebitda=250, pretax_income=180, net_income=150, eps=3,
            interest_expense=20,
        ),
        cashflow=CashFlow(operating_cash_flow=180, capex=-50, free_cash_flow=130),
        fiscal_date="2026-06-30",
    )


def test_risk_engine_integrates_altman():
    result = RiskEngine().calculate(statements(), market_value_equity=2000)
    assert 0 <= result.score <= 100
    assert result.altman_score is not None
    assert result.altman_classification == "Excelente"
    assert result.current_ratio == 400 / 150
    assert result.interest_coverage == 10


def test_missing_market_equity_does_not_fake_altman():
    result = RiskEngine().calculate(statements(), market_value_equity=None)
    assert result.altman_score is None
    assert result.altman_classification == "Datos insuficientes"
