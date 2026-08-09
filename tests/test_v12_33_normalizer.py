from investment_analyzer.providers.normalizer import ProviderNormalizer


def test_normalizes_yahoo_style_fields():
    x=ProviderNormalizer.canonical_fields({"regularMarketPrice":14.29,"marketCap":100,"expenseRatio":0.0009,"benchmarkName":"S&P 500"})
    assert x["price"]==14.29
    assert x["market_cap"]==100
    assert x["expense_ratio"]==0.0009
    assert x["benchmark"]=="S&P 500"


def test_normalizes_reit_fields():
    x=ProviderNormalizer.canonical_fields({"FFO":0.4541,"AFFO":0.41,"NAV":12.2})
    assert x=={"price":None,"market_cap":None,"expense_ratio":None,"benchmark":None,"holdings":None,"ffo":0.4541,"affo":0.41,"nav":12.2,"yield":None,"coupon":None,"maturity":None,"volume":None}
