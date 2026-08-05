from investment_analyzer.analysis.integration.fundamental_valuation_risk import FinancialAnalysisIntegrator
from investment_analyzer.common.models import BalanceSheet, CashFlow, FinancialStatements, IncomeStatement, PriceData
from investment_analyzer.pipeline.financial_modules import FinancialModuleAdapter
from investment_analyzer.analysis.context.analysis_context import AnalysisContext


def _asset():
    class Asset:
        financials = FinancialStatements(
            balance=BalanceSheet(total_assets=1000, current_assets=400, cash=100, inventory=50,
                                 receivables=100, total_liabilities=400, current_liabilities=200,
                                 long_term_debt=200, shareholders_equity=600, retained_earnings=300),
            income=IncomeStatement(revenue=1000, gross_profit=400, operating_income=200, ebit=200,
                                   ebitda=250, pretax_income=180, net_income=150, eps=3, interest_expense=20),
            cashflow=CashFlow(operating_cash_flow=180, capex=-50, free_cash_flow=130,
                              dividends_paid=-30, share_buybacks=-20),
            fiscal_date="2026-06-30")
        price = PriceData(symbol="TEST", price=100, market_cap=10000, shares_outstanding=100)
    return Asset()


def test_adapter_populates_context_from_real_engines():
    context = AnalysisContext(asset=_asset())
    result = FinancialModuleAdapter(integrator=FinancialAnalysisIntegrator()).run(context)
    assert 0 <= result["score"] <= 100
    assert context.risk["score"] >= 0
    assert "financial_integration" in context.metadata
