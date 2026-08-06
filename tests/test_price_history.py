from investment_analyzer.providers.yahoo_adapter import YahooFinanceAdapter


class FakeHistory:
    empty = False
    columns = ["Open", "High", "Low", "Close", "Volume"]
    index = ["2026-01-01", "2026-01-02", "2026-01-03"]

    def dropna(self, subset=None):
        return self

    def copy(self):
        return self

    def __getitem__(self, key):
        data = {
            "Open": [9, 10, 11],
            "High": [11, 12, 13],
            "Low": [8, 9, 10],
            "Close": [10, 11, 12],
            "Volume": [100, 110, 120],
        }
        return FakeSeries(data[key])


class FakeSeries:
    def __init__(self, values): self.values = values
    def fillna(self, value): return self
    def tolist(self): return self.values


class FakeTicker:
    def history(self, period="2y", interval="1d", auto_adjust=False):
        assert period == "2y"
        assert interval == "1d"
        return FakeHistory()


class FakeYF:
    def Ticker(self, symbol):
        assert symbol == "FMTY14.MX"
        return FakeTicker()


def test_price_history_returns_ohlcv_series():
    history = YahooFinanceAdapter(FakeYF()).price_history("fmty14.mx")
    assert history.symbol == "FMTY14.MX"
    assert len(history) == 3
    assert history.close == [10.0, 11.0, 12.0]
    assert history.volume == [100.0, 110.0, 120.0]
