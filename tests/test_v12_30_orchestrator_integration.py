from orchestrator import build_parser, parse_provider_symbols


def test_interactive_parser_has_no_required_symbol():
    assert build_parser().parse_args([]).symbol is None


def test_once_flag_and_provider_mapping():
    args=build_parser().parse_args(["--once","--provider-symbol","yahoo=FMTY14.MX"])
    assert args.once is True
    assert parse_provider_symbols(args.provider_symbol)=={"yahoo":"FMTY14.MX"}
