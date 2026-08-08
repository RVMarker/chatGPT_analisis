from investment_analyzer.cli.menu import choose_analysis


def test_choose_analysis_default(monkeypatch):
    monkeypatch.setattr("builtins.input",lambda _: "")
    assert choose_analysis()=="1"


def test_choose_analysis_modes(monkeypatch):
    values=iter(["2"])
    monkeypatch.setattr("builtins.input",lambda _: next(values))
    assert choose_analysis()=="2"
