from investment_analyzer.analysis.etf_analyzer import ETFAnalyzer


def test_sector_country_exposure_and_top3():
    r=ETFAnalyzer().analyze('ETF',{'holdings':[
        {'symbol':'A','weight':.30,'sector':'Tech','country':'US'},
        {'symbol':'B','weight':.20,'sector':'Tech','country':'US'},
        {'symbol':'C','weight':.10,'sector':'Health','country':'JP'},
    ],'expense_ratio':.001})
    assert r.exposure['sector'][0]==('Tech',50.0)
    assert r.exposure['country'][0]==('US',50.0)
    assert r.exposure['sector_top3_weight']==60.0
    assert r.exposure['country_top3_weight']==60.0
