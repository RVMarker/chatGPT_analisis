from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from .company import Company
from .exchange import Exchange
from .identifier import SecurityIdentifier


class Asset(BaseModel):

    asset_id: str

    symbol: str

    asset_type: str

    currency: str

    company: Company

    exchange: Exchange

    identifiers: SecurityIdentifier

    active: bool = True

    lot_size: int = 1

    price_multiplier: float = 1.0

    tick_size: Optional[float] = None