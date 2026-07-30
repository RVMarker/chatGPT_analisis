from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Company(BaseModel):

    name: str

    legal_name: Optional[str] = None

    sector: Optional[str] = None

    industry: Optional[str] = None

    country: Optional[str] = None

    website: Optional[str] = None

    employees: Optional[int] = None

    description: Optional[str] = None