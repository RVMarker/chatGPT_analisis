"""
Todas las reglas del Decision Engine.

Aquí NO existen votos.

Todo se convierte a un score entre 0 y 100.
"""


# ============================================================
# DCF
# ============================================================

def score_dcf(upside):

    if upside >= 60:
        return 100

    if upside >= 40:
        return 90

    if upside >= 25:
        return 80

    if upside >= 15:
        return 70

    if upside >= 5:
        return 60

    if upside >= -5:
        return 50

    if upside >= -15:
        return 35

    return 10


# ============================================================
# PE
# ============================================================

def score_pe(relative_pe):

    """
    relative_pe

    PE empresa / PE sector

    0.70 significa 30% descuento

    """

    if relative_pe <= .60:
        return 100

    if relative_pe <= .75:
        return 90

    if relative_pe <= .90:
        return 80

    if relative_pe <= 1.05:
        return 65

    if relative_pe <= 1.20:
        return 45

    return 20


# ============================================================
# EV EBITDA
# ============================================================

def score_ev(relative):

    if relative <= .60:
        return 100

    if relative <= .80:
        return 90

    if relative <= 1.00:
        return 75

    if relative <= 1.20:
        return 55

    return 20


# ============================================================
# ALTMAN
# ============================================================

def score_altman(z):

    if z >= 4:
        return 100

    if z >= 3:
        return 90

    if z >= 2.6:
        return 80

    if z >= 2:
        return 65

    if z >= 1.8:
        return 45

    return 10


# ============================================================
# PIOTROSKI
# ============================================================

def score_piotroski(score):

    return score * 11.11