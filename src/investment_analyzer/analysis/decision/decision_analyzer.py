# ==========================================================
# decision_analyzer.py
#
# Reemplaza completamente analisis_conclusion() de la V10
#
# NO utiliza votos.
# NO utiliza BUY/HOLD/SELL individuales.
#
# Produce:
#
# - Veredicto Estratégico
# - Veredicto Táctico
# - Nivel de confianza
# - Desglose por pesos
# - Fortalezas
# - Red Flags
# - Contra-tesis
#
# Compatible con el resto del proyecto.
# ==========================================================

from __future__ import annotations

from decision_engine import DecisionEngine


class DecisionAnalyzer:

    def __init__(self):

        self.engine = DecisionEngine()

    # ----------------------------------------------------------

    def build(

        self,

        fundamental_score,

        dcf_score,

        comparables_score,

        macro_score,

        risk_score,

        technical_score,

        sentiment_score,

        smart_money_score,

        provider_quality,

        freshness,

        consistency,

        completeness,

        strengths,

        red_flags,

        counter_thesis,

    ):

        strategic_scores = {

            "fundamental": fundamental_score,

            "valuation": dcf_score,

            "comparables": comparables_score,

            "macro": macro_score,

            "risk": risk_score,

        }

        tactical_scores = {

            "technical": technical_score,

            "sentiment": sentiment_score,

            "smart_money": smart_money_score,

            "macro": macro_score,

        }

        confidence_inputs = {

            "provider_quality": provider_quality,

            "freshness": freshness,

            "consistency": consistency,

            "completeness": completeness,

        }

        result = self.engine.evaluate(

            strategic_scores,

            tactical_scores,

            confidence_inputs,

            strengths=strengths,

            red_flags=red_flags,

        )

        report = {

            "strategic": result,

            "counter_thesis": counter_thesis,

        }

        return report