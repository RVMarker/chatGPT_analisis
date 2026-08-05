from investment_analyzer.pipeline.pipeline import AnalysisPipeline


class Recorder:
    def __init__(self, name, calls):
        self.name, self.calls = name, calls

    def run(self, context):
        self.calls.append(self.name)
        return {"score": 50}


class Asset:
    def load(self, ticker):
        return {"ticker": ticker}


class Decision:
    def run(self, context):
        assert context.fundamentals == {"score": 50}
        assert context.valuation == {"score": 50}
        assert context.risk == {"score": 50}
        return {"strategic": "MANTENER", "tactical": "MANTENER"}


class Modules:
    def __init__(self, calls):
        self.asset = Asset()
        self.technical = Recorder("technical", calls)
        self.fundamental = Recorder("fundamental", calls)
        self.valuation = Recorder("valuation", calls)
        self.risk = Recorder("risk", calls)
        self.comparables = Recorder("comparables", calls)
        self.sentiment = Recorder("sentiment", calls)
        self.macro = Recorder("macro", calls)
        self.porter = Recorder("porter", calls)
        self.elliott = Recorder("elliott", calls)
        self.dow = Recorder("dow", calls)
        self.backtest = Recorder("backtest", calls)
        self.decision = Decision()


def test_pipeline_runs_modules_in_dependency_order():
    calls = []
    context = AnalysisPipeline(providers=None, modules=Modules(calls)).run("FMTY14.MX")
    assert context.asset == {"ticker": "FMTY14.MX"}
    assert calls == [
        "technical", "fundamental", "valuation", "risk", "comparables",
        "sentiment", "macro", "porter", "elliott", "dow", "backtest",
    ]
    assert context.decision["strategic"] == "MANTENER"
