"""
Clase base para todos los módulos de análisis.
"""

from __future__ import annotations

from abc import ABC

from abc import abstractmethod


class AnalysisModule(ABC):

    @abstractmethod

    def run(

        self,

        context,

    ):

        raise NotImplementedError()