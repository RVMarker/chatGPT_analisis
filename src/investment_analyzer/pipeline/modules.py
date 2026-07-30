"""
Contenedor de módulos.

Permite reemplazar fácilmente cualquier motor.
"""


class Modules:

    def __init__(

        self,

        asset,

        technical,

        fundamental,

        valuation,

        risk,

        comparables,

        sentiment,

        macro,

        porter,

        elliott,

        dow,

        backtest,

        decision,

    ):

        self.asset = asset

        self.technical = technical

        self.fundamental = fundamental

        self.valuation = valuation

        self.risk = risk

        self.comparables = comparables

        self.sentiment = sentiment

        self.macro = macro

        self.porter = porter

        self.elliott = elliott

        self.dow = dow

        self.backtest = backtest

        self.decision = decision