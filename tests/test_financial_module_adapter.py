from investment_analyzer.analysis.integration.fundamental_valuation_risk import FinancialAnalysisIntegrator
from investment_analyzer.common.models import BalanceSheet, CashFlow, FinancialStatements, IncomeStatement, PriceData
from investment_analyzer.pipeline.financial_modules import FinancialModuleAdapter
from investment_analyzer.analysis.context.analysis_context import AnalysisContext


def _context(kind="STOCK", ffo_proxy=None):
    Asset = type("Asset", (), {"symbol": "TEST", "asset_type": kind})
    financials = FinancialStatements(
        balance=BalanceSheet(total_assets=1000, current_assets=400, cash=100, inventory=50,
                             receivables=100, total_liabilities=400, current_liabilities=200,
                             long_term_debt=200, shareholders_equity=600, retained_earnings=300),
        income=IncomeStatement(revenue=1000, gross_profit=400, operating_income=200, ebit=200,
                               ebitda=250, pretax_income=180, net_income=150, eps=3, interest_expense=20),
        cashflow=CashFlow(operating_cash_flow=180, capex=-50, free_cash_flow=130,
                          dividends_paid=-30, share_buybacks=-20,
                          depreciation_amortization=40, property_gain_loss=0,
                          ffo_proxy=ffo_proxy),
        fiscal_date="2026-06-30")
    price = PriceData(symbol="TEST", current=100, market_cap=10000, shares_outstanding=100)
    return AnalysisContext(asset=Asset(), price=price, financials=financials)


def test_adapter_populates_context_from_real_engines():
    context = _context()
    result = FinancialModuleAdapter(integrator=FinancialAnalysisIntegrator()).run(context)
    assert result is context
    assert 0 <= context.fundamentals["score"] <= 100
    assert 0 <= context.risk["score"] <= 100
    assert "financial_integration" in context.metadata


def test_adapter_routes_fibra_to_reit_valuation():
    context = _context(kind="REIT", ffo_proxy=300)
    FinancialModuleAdapter(integrator=FinancialAnalysisIntegrator()).run(context)
    assert context.valuation["available"] is True
    assert context.valuation["model"] == "FFO_CAPITALIZATION"
    assert context.valuation["source_quality"] == "FFO_PROXY"
    assert context.metadata["financial_integration"]["asset_type"] == "REIT"
