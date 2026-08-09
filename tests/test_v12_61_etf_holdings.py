from investment_analyzer.analysis.etf_holdings import ETFCompositionAnalyzer


def test_top10_and_weights_are_normalized():
    holdings=[{'symbol':f'S{i}','weight':i} for i in range(1,13)]
    r=ETFCompositionAnalyzer().analyze(holdings=holdings,expense_ratio=.002)
    assert len(r.holdings)==12
    assert r.holdings[0]['rank']==1
    assert r.top10_weight is not None
    assert abs(r.top10_weight-sum(range(3,13))/100)<1e-9


def test_missing_etf_composition_is_explicit():
    r=ETFCompositionAnalyzer().analyze(expense_ratio=.005)
    assert r.holdings==[]
    assert any('Composición' in w for w in r.warnings)
