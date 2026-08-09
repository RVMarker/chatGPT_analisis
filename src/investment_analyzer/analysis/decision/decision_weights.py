"""Pesos oficiales del Decision Engine V12.81.

REGLA: comparables y macro NO votan en el veredicto. Son contexto.
El veredicto estratégico usa exactamente 35/30/20/15.
"""

# Horizonte estratégico: años.
# Technical se conserva aquí como componente de riesgo/entrada, mientras
# comparables y macro permanecen fuera del voto.
STRATEGIC = {
    "fundamental": 0.35,
    "valuation": 0.30,
    "technical": 0.20,
    "risk": 0.15,
}

# Horizonte táctico: semanas. Ningún factor macro/comparable vota.
TACTICAL = {
    "technical": 0.45,
    "sentiment": 0.30,
    "smart_money": 0.25,
}

CONTEXTUAL = {
    "comparables": 0.0,
    "peer_valuation": 0.0,
    "macro": 0.0,
    "interest_rate_context": 0.0,
}


def validate_weights() -> None:
    for name, weights in (("STRATEGIC", STRATEGIC), ("TACTICAL", TACTICAL)):
        total = sum(weights.values())
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"{name} debe sumar 1.0; obtuvo {total:.6f}")


validate_weights()
