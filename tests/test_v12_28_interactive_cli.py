from orchestrator import ask_symbol, build_parser


def test_symbol_argument_is_optional():
    args=build_parser().parse_args([])
    assert args.symbol is None


def test_symbol_argument_still_supported():
    args=build_parser().parse_args(["FMTY14.MX"])
    assert args.symbol == "FMTY14.MX"
