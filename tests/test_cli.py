from investment_analyzer.cli import run_cli


class FakePipeline:
    def run(self, ticker):
        assert ticker == "FMTY14.MX"
        return {"ticker": ticker}


def test_run_cli_prints_report(monkeypatch, capsys):
    monkeypatch.setattr(
        "investment_analyzer.cli.format_decision_report",
        lambda context: f"REPORT {context['ticker']}",
    )
    assert run_cli("FMTY14.MX", FakePipeline()) == 0
    assert "REPORT FMTY14.MX" in capsys.readouterr().out
