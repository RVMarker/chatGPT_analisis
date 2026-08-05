"""Pesos oficiales del Decision Engine V11.

Importante: comparables y macro NO forman parte del score del veredicto.
Se conservan como contexto explicativo para el analista (valor relativo,
condiciones de tasas y margen de seguridad exigido).
"""

# Horizonte estratégico: años.
# Solo factores que representan tesis fundamental/valoración/riesgo.
STRATEGIC = {
    "fundamental": 0.40,
    "valuation": 0.40,
    "risk": 0.20,
}

# Horizonte táctico: semanas.
# Macro queda fuera del score; sirve como contexto, no como voto.
TACTICAL = {
    "technical": 0.60,
    "sentiment": 0.20,
    "smart_money": 0.20,
}

CONTEXTUAL = {
    "comparables": 0.0,
    "macro": 0.0,
}


def validate_weights() -> None:
    """Fail fast if a decision category is accidentally misweighted."""
    for name, weights in (("STRATEGIC", STRATEGIC), ("TACTICAL", TACTICAL)):
        total = sum(weights.values())
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"{name} debe sumar 1.0; obtuvo {total:.6f}")


validate_weights()
