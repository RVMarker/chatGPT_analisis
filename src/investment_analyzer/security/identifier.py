from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class SecurityIdentifier(BaseModel):
    """
    Different identifiers that may represent the same security.
    """

    ticker: str

    yahoo: Optional[str] = None

    fmp: Optional[str] = None

    alpha_vantage: Optional[str] = None

    polygon: Optional[str] = None

    finnhub: Optional[str] = None

    isin: Optional[str] = None

    figi: Optional[str] = None

    cusip: Optional[str] = None

    sedol: Optional[str] = None

    lei: Optional[str] = None