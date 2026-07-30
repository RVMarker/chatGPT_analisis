"""
Generador de Red Flags.
"""


def detect(

    altman,

    debt_growth,

    dilution,

    insider_sales,

    sentiment,

):

    flags = []

    if altman < 2:

        flags.append(

            "Altman Z inferior a 2"

        )

    if debt_growth > 25:

        flags.append(

            "La deuda aumentó significativamente"

        )

    if dilution > 3:

        flags.append(

            "Dilución de acciones"

        )

    if insider_sales:

        flags.append(

            "Ventas recientes de insiders"

        )

    if sentiment < -.25:

        flags.append(

            "Sentimiento negativo en noticias"

        )

    return flags