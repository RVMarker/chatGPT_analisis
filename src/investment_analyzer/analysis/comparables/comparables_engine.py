"""Peer valuation context for V11.

Comparables are explicitly contextual: they do not contribute to the
DecisionEngine score. They help explain relative valuation and the strategic
thesis.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from statistics import median
from typing import Any, Iterable


@dataclass(slots=True)
class ComparableResult:
    pe: float | None
    ev_ebitda: float | None
    peer_pe_median: float | None
    peer_ev_ebitda_median: float | None
    pe_premium_discount: float | None
    ev_ebitda_premium_discount: float | None
    context: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class ComparablesEngine:
    @staticmethod
    def _clean(values: Iterable[float | None]) -> list[float]:
        return [float(v) for v in values if v is not None and float(v) > 0]

    @staticmethod
    def _relative(asset: float | None, peer: float | None) -> float | None:
        if asset is None or peer in (None, 0):
            return None
        return float(asset) / float(peer) - 1.0

    def calculate(
        self,
        *,
        pe: float | None = None,
        ev_ebitda: float | None = None,
        peer_pe: Iterable[float | None] = (),
        peer_ev_ebitda: Iterable[float | None] = (),
    ) -> ComparableResult:
        pe_peers = self._clean(peer_pe)
        ev_peers = self._clean(peer_ev_ebitda)
        pe_median = median(pe_peers) if pe_peers else None
        ev_median = median(ev_peers) if ev_peers else None
        pe_rel = self._relative(pe, pe_median)
        ev_rel = self._relative(ev_ebitda, ev_median)

        parts = []
        if pe_rel is not None:
            parts.append(f"P/E {pe_rel:+.1%} vs mediana de peers")
        if ev_rel is not None:
            parts.append(f"EV/EBITDA {ev_rel:+.1%} vs mediana de peers")
        context = "; ".join(parts) if parts else "Datos comparables insuficientes"
        return ComparableResult(pe, ev_ebitda, pe_median, ev_median, pe_rel, ev_rel, context)
