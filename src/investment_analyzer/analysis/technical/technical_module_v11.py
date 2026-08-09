"""Historical Technical Analysis V12.

Consumes PriceHistory and produces a transparent technical score plus the
actual market levels required by the executable trade plan.
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
                module="technical", score=None,
                explanation="Histórico insuficiente para el análisis técnico V12.",
                warnings=[f"Se requieren al menos {self.min_history} observaciones; disponibles: {len(history)}."],
                metadata={"available": False, "history_length": len(history), "indicators": {}, "requirements": {}, "component_scores": {}, "available_components": [], "unavailable_components": list(self.weights)},
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
        else: available["trend"] = False
        rsi = ind["rsi14"]
        if rsi is not None:
            scores["momentum"] = 70.0 if 50 <= rsi <= 70 else 55.0 if rsi >= 40 else 30.0
            available["momentum"] = True
        else: available["momentum"] = False
        macd_data = ind["macd"]
        if macd_data is not None:
            scores["macd"] = 75.0 if macd_data["macd"] > macd_data["signal"] else 30.0
            available["macd"] = True
        else: available["macd"] = False
        bb = ind["bollinger20"]
        if bb is not None:
            position = (last - bb["lower"]) / (bb["upper"] - bb["lower"]) if bb["upper"] != bb["lower"] else 0.5
            scores["volatility"] = 70.0 if 0.40 <= position <= 0.80 else 55.0 if position > 0.20 else 35.0
            available["volatility"] = True
        else: available["volatility"] = False
        if sma50 is not None and sma200 is not None:
            scores["long_term"] = 80.0 if last > sma50 > sma200 else 65.0 if last > sma200 else 30.0
            available["long_term"] = True
        else: available["long_term"] = False

        available_weight = sum(self.weights[k] for k in self.weights if available.get(k) and k in scores)
        score = None if available_weight <= 0 else round(sum(scores[k] * self.weights[k] for k in self.weights if available.get(k) and k in scores) / available_weight, 2)
        warnings = [f"Indicador no disponible: {k}" for k, ok in available.items() if not ok]
        technical = TechnicalIndicators(rsi=rsi, macd=macd_data["macd"] if macd_data else None, signal=macd_data["signal"] if macd_data else None, atr=ind["atr14"], sma20=sma20, sma50=sma50, sma200=sma200, ema20=ema20, bollinger_position=((last - bb["lower"]) / (bb["upper"] - bb["lower"]) if bb and bb["upper"] != bb["lower"] else None))

        window = min(20, len(history.close))
        lows = history.low[-window:] if history.low else history.close[-window:]
        highs = history.high[-window:] if history.high else history.close[-window:]
        support = min(float(x) for x in lows if x is not None and float(x) > 0) if lows else None
        resistance = max(float(x) for x in highs if x is not None and float(x) > 0) if highs else None
        atr = ind["atr14"]
        # A structural level is preferable; ATR is a secondary fallback in trade_plan.
        if support is not None and support >= last:
            support = None
        if resistance is not None and resistance <= last:
            resistance = None

        return AnalysisResult(
            module="technical", score=score,
            explanation="Score técnico V12 calculado sobre histórico OHLCV; componentes ausentes excluidos y pesos renormalizados.",
            warnings=warnings,
            metadata={
                "available": score is not None, "history_length": len(history), "indicators": technical,
                "requirements": req, "component_scores": scores,
                "available_components": [k for k, ok in available.items() if ok],
                "unavailable_components": [k for k, ok in available.items() if not ok],
                "effective_weight": available_weight,
                "support": support, "resistance": resistance, "atr": atr,
                "support_method": "20_period_low", "resistance_method": "20_period_high",
            },
        )
