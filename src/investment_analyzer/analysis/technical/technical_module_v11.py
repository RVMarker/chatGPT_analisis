"""Historical Technical Analysis V11.

Consumes PriceHistory and produces a transparent technical score. It does not
invent indicators when history is insufficient.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from investment_analyzer.analysis.technical.technical_indicators import calculate_indicators
from investment_analyzer.common.models import AnalysisResult, PriceHistory, TechnicalIndicators


@dataclass(slots=True)
class TechnicalAnalysisV11:
    min_history: int = 34
    weights: dict[str, float] = field(default_factory=lambda: {
        "trend": 0.30,
        "momentum": 0.25,
        "macd": 0.20,
        "volatility": 0.15,
        "long_term": 0.10,
    })

    def analyze(self, history: PriceHistory) -> AnalysisResult:
        if len(history) < self.min_history:
            return AnalysisResult(
                module="technical",
                score=50.0,
                explanation="Histórico insuficiente para el análisis técnico V11.",
                warnings=[f"Se requieren al menos {self.min_history} observaciones; disponibles: {len(history)}."],
                metadata={"available": False, "history_length": len(history), "indicators": {}, "requirements": {}},
            )

        ind = calculate_indicators(history)
        req = ind["requirements"]
        scores = {}
        available = {}

        ema20, sma20, sma50, sma200 = ind["ema20"], ind["sma20"], ind["sma50"], ind["sma200"]
        last = history.close[-1]
        if ema20 is not None and sma20 is not None:
            scores["trend"] = 100.0 if last > ema20 > sma20 else 65.0 if last > ema20 else 35.0
            available["trend"] = True
        else:
            scores["trend"] = 50.0; available["trend"] = False

        rsi = ind["rsi14"]
        if rsi is not None:
            scores["momentum"] = 70.0 if 50 <= rsi <= 70 else 55.0 if rsi >= 40 else 30.0
            available["momentum"] = True
        else:
            scores["momentum"] = 50.0; available["momentum"] = False

        macd_data = ind["macd"]
        if macd_data is not None:
            scores["macd"] = 75.0 if macd_data["macd"] > macd_data["signal"] else 30.0
            available["macd"] = True
        else:
            scores["macd"] = 50.0; available["macd"] = False

        bb = ind["bollinger20"]
        if bb is not None:
            position = (last - bb["lower"]) / (bb["upper"] - bb["lower"]) if bb["upper"] != bb["lower"] else 0.5
            scores["volatility"] = 70.0 if 0.40 <= position <= 0.80 else 55.0 if position > 0.20 else 35.0
            available["volatility"] = True
        else:
            scores["volatility"] = 50.0; available["volatility"] = False

        if sma50 is not None and sma200 is not None:
            scores["long_term"] = 80.0 if last > sma50 > sma200 else 65.0 if last > sma200 else 30.0
            available["long_term"] = True
        else:
            scores["long_term"] = 50.0; available["long_term"] = False

        score = sum(scores[k] * self.weights[k] for k in self.weights)
        warnings = [f"Indicador no disponible: {k}" for k, ok in available.items() if not ok]
        technical = TechnicalIndicators(
            rsi=rsi,
            macd=macd_data["macd"] if macd_data else None,
            signal=macd_data["signal"] if macd_data else None,
            atr=ind["atr14"],
            sma20=sma20,
            sma50=sma50,
            sma200=sma200,
            ema20=ema20,
            bollinger_position=((last - bb["lower"]) / (bb["upper"] - bb["lower"]) if bb and bb["upper"] != bb["lower"] else None),
        )
        return AnalysisResult(
            module="technical", score=round(score, 2),
            explanation="Score técnico V11 calculado sobre histórico OHLCV.",
            warnings=warnings,
            metadata={"available": True, "history_length": len(history), "indicators": technical, "requirements": req, "component_scores": scores},
        )
