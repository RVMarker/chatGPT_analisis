from __future__ import annotations

from pydantic import BaseModel


class Exchange(BaseModel):

    code: str

    name: str

    country: str

    currency: str

    timezone: str