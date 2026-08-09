from investment_analyzer.analysis.stock_integration import StockAnalyzer


def test_stock_strategic_tactical_scores_and_dcf():
    r=StockAnalyzer().analyze("AAPL",{"price":200,"dcf_value":240,"roe":.30,"roic":.25,"revenue_growth":8,"earnings_growth":10,"debt_equity":1,"dividend_yield":2,"technical_score":70,"momentum":75,"trend":80,"volatility":15,"liquidity":90})
    assert r["fair_value"]==240
    assert r["margin_of_safety"]==20
    assert r["strategic_coverage"]==100
    assert r["tactical_coverage"]==100


def test_stock_relative_valuation_is_fallback_only():
    r=StockAnalyzer().analyze("XYZ",{"price":100,"pe":20,"peer_pe":15})
    assert r["fair_value"]==75
    assert r["warnings"]
