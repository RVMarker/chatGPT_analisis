"""
Clase base para cualquier proveedor.

Yahoo

FMP

Polygon

Alpha

etc.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class ProviderBase(ABC):

    NAME = ""

    # ----------------------------------------------------

    @abstractmethod
    def get_price(

        self,

        symbol: str,

    ):
        pass

    # ----------------------------------------------------

    @abstractmethod
    def get_balance_sheet(

        self,

        symbol: str,

    ):
        pass

    # ----------------------------------------------------

    @abstractmethod
    def get_income_statement(

        self,

        symbol: str,

    ):
        pass

    # ----------------------------------------------------

    @abstractmethod
    def get_cash_flow(

        self,

        symbol: str,

    ):
        pass

    # ----------------------------------------------------

    @abstractmethod
    def get_company(

        self,

        symbol: str,

    ):
        pass

    # ----------------------------------------------------

    @abstractmethod
    def get_news(

        self,

        symbol: str,

    ):
        pass