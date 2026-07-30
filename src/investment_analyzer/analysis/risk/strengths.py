"""
Fortalezas automáticas.
"""


def detect(

    roic,

    margin,

    altman,

    piotroski,

    upside,

):

    strengths = []

    if roic > 15:

        strengths.append(

            "ROIC elevado"

        )

    if margin > 20:

        strengths.append(

            "Margen operativo sólido"

        )

    if altman > 3:

        strengths.append(

            "Excelente salud financiera"

        )

    if piotroski >= 8:

        strengths.append(

            "Piotroski muy alto"

        )

    if upside > 30:

        strengths.append(

            "Amplio margen de seguridad"

        )

    return strengths