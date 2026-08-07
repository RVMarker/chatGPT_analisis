"""Production peer valuation context for V11.

Comparables are contextual only: they never enter DecisionEngine voting.
Peer symbols are explicit and can be extended without changing the engine.
"""
from __future__ import annotations

from typing import Any

from investment_analyzer.analysis.comparables.comparables_engine import ComparablesEngine


DEFAULT_PEERS: dict[str, tuple[str, ...]] = {
    "FMTY14.MX": ("FUNO11.MX", "DANHOS13.MX", "FIBRAMQ12.MX"),
}


class ProductionComparablesModule:
    def __init__(self, provider_manager, peers: dict[str, tuple[str, ...]] | None = None):
        self.provider_manager = provider_manager
        self.peers = peers or DEFAULT_PEERS
        self.engine = ComparablesEngine()

    @staticmethod
    def _metric(info: Any, *keys: str) -> float | None:
        if not isinstance(info, dict):
            return None
        for key in keys:
            value = info.get(key)
            if value is not None:
                try:
                    value = float(value)
                    if value > 0:
                        return value
                except (TypeError, ValueError):
                    pass
        return None

    def run(self, context):
        symbol = getattr(context.asset, "symbol", "")
        target = self.provider_manager.execute_with_fallback(symbol, "get_company")
        if not target.success:
            return {"available": False, "score": None, "reason": target.error or "No se obtuvo información del activo", "evidence": []}

        target_info = target.data or {}
        target_pe = self._metric(target_info, "trailingPE", "forwardPE")
        target_ev = self._metric(target_info, "enterpriseToEbitda", "enterpriseToEbitda")
        peer_records = []
        peer_pe = []
        peer_ev = []
        for peer in self.peers.get(symbol, ()):
            response = self.provider_manager.execute_with_fallback(peer, "get_company")
            if not response.success:
                continue
            info = response.data or {}
            pe = self._metric(info, "trailingPE", "forwardPE")
            ev = self._metric(info, "enterpriseToEbitda")
            if pe is not None: peer_pe.append(pe)
            if ev is not None: peer_ev.append(ev)
            peer_records.append({"symbol": peer, "pe": pe, "ev_ebitda": ev, "provider": response.provider, "provider_symbol": response.provider_symbol})

        result = self.engine.calculate(pe=target_pe, ev_ebitda=target_ev, peer_pe=peer_pe, peer_ev_ebitda=peer_ev)
        return {
            "available": bool(peer_pe or peer_ev),
            "score": None,
            "pe": result.pe,
            "ev_ebitda": result.ev_ebitda,
            "peer_pe_median": result.peer_pe_median,
            "peer_ev_ebitda_median": result.peer_ev_ebitda_median,
            "pe_premium_discount": result.pe_premium_discount,
            "ev_ebitda_premium_discount": result.ev_ebitda_premium_discount,
            "context": result.context,
            "peers": peer_records,
            "provider": target.provider,
            "provider_symbol": target.provider_symbol,
        }
