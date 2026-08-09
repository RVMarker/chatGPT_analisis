from investment_analyzer.analysis.asset_normalizer import AssetDataNormalizer


def test_normalizer_maps_yahoo_and_domain_fields():
    r=AssetDataNormalizer().normalize({'regularMarketPrice':14.29,'marketCap':1000000,'trailingPE':27.98,'financials':{'ffoPerShare':.4541},'metadata':{'dividendYield':.08}})
    assert r['price']==14.29
    assert r['market_cap']==1000000
    assert r['pe']==27.98
    assert r['ffo_share']==.4541
    assert r['dividend_yield']==.08


def test_normalizer_does_not_invent_missing_values():
    r=AssetDataNormalizer().normalize({'price':10})
    assert r['price']==10
    assert 'ffo_share' not in r
