from investment_analyzer.providers.symbol_resolver import SymbolResolver


def test_provider_mapping_does_not_mutate_canonical_symbol():
    resolver = SymbolResolver()
    resolver.register(" fmty14.mx ", "fmp", "FMTY14")
    resolver.register("FMTY14.MX", "polygon", "FMTY14")

    fmp = resolver.resolve("fmtY14.mx", "FMP")
    yahoo = resolver.resolve("FMTY14.MX", "yahoo")

    assert fmp.canonical == "FMTY14.MX"
    assert fmp.symbol == "FMTY14"
    assert fmp.source == "explicit_mapping"
    assert yahoo.canonical == "FMTY14.MX"
    assert yahoo.symbol == "FMTY14.MX"
    assert yahoo.source == "canonical_fallback"
