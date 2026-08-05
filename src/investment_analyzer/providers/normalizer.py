"""Normalización común de respuestas de proveedores.

El ticker canónico del sistema es el ticker introducido para Yahoo Finance.
Cada proveedor puede usar otro identificador, pero el resto de la aplicación
nunca debe depender de esa nomenclatura externa.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from investment_analyzer.common.models import ProviderResult


class ProviderNormalizer:
    """Convierte respuestas heterogéneas en estructuras auditables."""

    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)

    @classmethod
    def result(
        cls,
        provider: str,
        payload: Any,
        *,
        success: bool = True,
        latency_ms: float = 0.0,
    ) -> ProviderResult:
        return ProviderResult(
            provider=provider,
            timestamp=cls._utcnow(),
            success=success,
            latency_ms=max(0.0, float(latency_ms)),
            payload=payload,
        )

    @staticmethod
    def first_value(data: Mapping[str, Any] | None, *keys: str, default=None):
        if not data:
            return default
        for key in keys:
            value = data.get(key)
            if value is not None:
                return value
        return default

    @staticmethod
    def freshness(timestamp: datetime | None, now: datetime | None = None) -> float:
        """Return a 0-100 freshness score; newer data gets a higher score."""
        if timestamp is None:
            return 0.0
        now = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        age_days = max(0.0, (now - timestamp).total_seconds() / 86400.0)
        if age_days <= 1:
            return 100.0
        if age_days <= 7:
            return 90.0
        if age_days <= 30:
            return 75.0
        if age_days <= 90:
            return 55.0
        if age_days <= 365:
            return 30.0
        return 10.0
