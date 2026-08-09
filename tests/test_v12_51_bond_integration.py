from investment_analyzer.analysis.bond_integration import BondAnalyzer


def test_bond_adapter_maps_common_provider_fields():
    r=BondAnalyzer().analyze("M10",{"market_price":98,"par_value":100,"couponRate":.08,"ytm":.07,"years_to_maturity":5,"duration":4,"creditScore":90,"liquidityScore":80,"inflation":3,"spread":2,"momentum":60})
    assert r["symbol"]=="M10"
    assert r["fair_price"] is not None
    assert r["strategic_coverage"]==100
    assert r["tactical_coverage"]==100


def test_missing_bond_fields_remain_missing():
    r=BondAnalyzer().analyze("M10",{"market_price":100})
    assert r["fair_price"] is None
    assert r["warnings"]
