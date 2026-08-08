from types import SimpleNamespace

from investment_analyzer.analysis.decision.decision_engine import DecisionEngine
from investment_analyzer.pipeline.actionable_report import render_actionable_layer


def _context():
    decision = DecisionEngine().evaluate(
        strategic_scores={"fundamental": 30, "valuation": 10, "risk": 35},
        tactical_scores={"technical": 55, "sentiment": 50, "smart_money": 60},
        confidence_inputs={
            "provider_quality": 95,
            "freshness": 95,
            "consistency": 90,
            "completeness": 95,
            "technical_data_quality": 90,
            "valuation_quality": "LOW_MEDIUM",
        },
        contextual={"comparables": 80, "macro": 60},
    )
    return SimpleNamespace(
        decision=decision,
        valuation={
            "sensitivity": {
                "base_case": {"yield": .09, "growth": .03, "fair_value": 7.8},
                "min_fair_value": 5.0,
                "max_fair_value": 14.0,
                "classifications": {
                    "0.0800": {"0.0200": "DESFAVORABLE", "0.0300": "NEUTRAL"},
                    "0.0900": {"0.0300": "DESFAVORABLE"},
                },
            }
        },
    )


def test_actionable_layer_explains_action_and_context():
    text = render_actionable_layer(_context())
    assert "DECISIÓN ACCIONABLE — V11.7" in text
    assert "ESTRATÉGICO" in text
    assert "VENDER" in text
    assert "FACTORES DECISIVOS — SÍ VOTAN" in text
    assert "FACTORES CONTEXTUALES — NO VOTAN" in text
    assert "ROBUSTEZ DE VALORACIÓN — SENSIBILIDAD" in text
    assert "REDUCIR EXPOSICIÓN" in text


def test_actionable_layer_never_turns_missing_data_into_a_positive_signal():
    context = _context()
    context.decision.missing_factors.append("AFFO: sin dato decisorio")
    text = render_actionable_layer(context)
    assert "AFFO: sin dato decisorio" in text
