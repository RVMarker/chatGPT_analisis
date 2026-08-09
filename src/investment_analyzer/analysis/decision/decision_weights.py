"""Pesos oficiales del Decision Engine V12.

Los pesos son transparentes y forman parte del contrato de decisión.
Comparables y macro son exclusivamente contextuales y nunca votan.
"""

# Horizonte estratégico: años.
STRATEGIC = {
    "fundamental": 0.35,
    "valuation": 0.30,
    "technical": 0.20,
    "risk": 0.15,
}

# Horizonte táctico: semanas.
TACTICAL = {
    "technical": 0.45,
    "sentiment": 0.30,
    "smart_money": 0.25,
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
