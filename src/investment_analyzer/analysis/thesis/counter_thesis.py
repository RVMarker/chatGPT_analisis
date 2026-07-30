"""
Generador de contra-tesis.

La idea es responder automáticamente:

¿Por qué podría estar equivocado el análisis?
"""


def generate(

    dcf_upside,

    relative_pe,

    altman,

    macro_score,

):

    thesis = []

    if dcf_upside > 40:

        thesis.append(

            "El mercado podría estar descontando un deterioro estructural aún no reflejado en el DCF."

        )

    if relative_pe < .80:

        thesis.append(

            "El descuento frente al sector podría estar justificado por menores expectativas de crecimiento."

        )

    if altman < 2.5:

        thesis.append(

            "La fortaleza financiera es inferior a la de empresas comparables."

        )

    if macro_score < 50:

        thesis.append(

            "Un entorno prolongado de tasas altas podría reducir la valoración objetivo."

        )

    return thesis