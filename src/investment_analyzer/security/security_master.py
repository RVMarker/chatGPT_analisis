"""
security_master.py
Investment Analyzer v11

Security Master

Mantiene una única representación interna del activo y traduce
automáticamente los símbolos para cada proveedor.

Nunca consulta Internet.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from dataclasses import dataclass


@dataclass(slots=True)
class Security:
    asset_id: str
    canonical_symbol: str
    name: str
    exchange: str
    currency: str
    asset_type: str
    yahoo: str
    fmp: str | None = None
    alpha_vantage: str | None = None
    polygon: str | None = None
    finnhub: str | None = None
    isin: str | None = None
    figi: str | None = None


class SecurityMaster:
    def __init__(self, database: str = "database/security_master.db"):
        Path(database).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(database)
        self.connection.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self):
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS securities(
                asset_id TEXT PRIMARY KEY,
                canonical_symbol TEXT UNIQUE,
                name TEXT,
                exchange TEXT,
                currency TEXT,
                asset_type TEXT,
                yahoo TEXT,
                fmp TEXT,
                alpha_vantage TEXT,
                polygon TEXT,
                finnhub TEXT,
                isin TEXT,
                figi TEXT
            )
        """)
        self.connection.commit()

    def add(self, security: Security):
        self.connection.execute("""
            INSERT OR REPLACE INTO securities(
                asset_id, canonical_symbol, name, exchange, currency, asset_type,
                yahoo, fmp, alpha_vantage, polygon, finnhub, isin, figi
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            security.asset_id, security.canonical_symbol, security.name,
            security.exchange, security.currency, security.asset_type,
            security.yahoo, security.fmp, security.alpha_vantage, security.polygon,
            security.finnhub, security.isin, security.figi,
        ))
        self.connection.commit()

    def seed_production_defaults(self):
        """Seed only deterministic, explicitly-known production mappings.

        This is deliberately separate from ``AssetLoader`` so an empty test
        SecurityMaster still treats unknown symbols as UNKNOWN. The production
        composition root calls this method before running the CLI.
        """
        existing = self.get("FMTY14.MX")
        if existing is None:
            self.add(Security(
                asset_id="AST-FMTY14",
                canonical_symbol="FMTY14.MX",
                name="Fibra Mty",
                exchange="BMV",
                currency="MXN",
                asset_type="REIT",
                yahoo="FMTY14.MX",
                fmp="FMTY14",
                polygon="FMTY14:BMV",
            ))

    def get(self, symbol: str) -> Security | None:
        row = self.connection.execute("""
            SELECT * FROM securities
            WHERE canonical_symbol=? OR yahoo=? OR fmp=? OR polygon=?
               OR alpha_vantage=? OR finnhub=? OR isin=? OR figi=?
        """, (symbol, symbol, symbol, symbol, symbol, symbol, symbol, symbol)).fetchone()
        if row is None:
            return None
        return Security(
            asset_id=row["asset_id"], canonical_symbol=row["canonical_symbol"],
            name=row["name"], exchange=row["exchange"], currency=row["currency"],
            asset_type=row["asset_type"], yahoo=row["yahoo"], fmp=row["fmp"],
            alpha_vantage=row["alpha_vantage"], polygon=row["polygon"],
            finnhub=row["finnhub"], isin=row["isin"], figi=row["figi"],
        )

    def provider_symbol(self, symbol: str, provider: str) -> str:
        security = self.get(symbol)
        if security is None:
            return symbol
        match provider.lower():
            case "yahoo":
                return security.yahoo
            case "fmp":
                return security.fmp or security.yahoo
            case "polygon":
                return security.polygon or security.yahoo
            case "alpha_vantage":
                return security.alpha_vantage or security.yahoo
            case "finnhub":
                return security.finnhub or security.yahoo
        return security.yahoo

    def exists(self, symbol: str) -> bool:
        return self.get(symbol) is not None

    def list_all(self):
        rows = self.connection.execute("SELECT * FROM securities ORDER BY canonical_symbol")
        return [dict(r) for r in rows]

    def delete(self, symbol: str):
        self.connection.execute("DELETE FROM securities WHERE canonical_symbol=?", (symbol,))
        self.connection.commit()

    def close(self):
        self.connection.close()
