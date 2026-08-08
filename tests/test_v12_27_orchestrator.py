from orchestrator import parse_provider_symbols

def test_provider_symbol_arguments():
    assert parse_provider_symbols(["yahoo=FMTY14.MX","provider_x=FMTY14"]) == {"yahoo":"FMTY14.MX","provider_x":"FMTY14"}

def test_invalid_provider_symbol_argument():
    try: parse_provider_symbols(["FMTY14.MX"])
    except ValueError as exc: assert "PROVIDER=SYMBOL" in str(exc)
    else: raise AssertionError("Expected ValueError")
