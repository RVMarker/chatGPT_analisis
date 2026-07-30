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


# ============================================================
# MODELO
# ============================================================

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


# ============================================================
# SECURITY MASTER
# ============================================================

class SecurityMaster:

    def __init__(

        self,

        database: str = "database/security_master.db",

    ):

        Path(database).parent.mkdir(

            parents=True,

            exist_ok=True,

        )

        self.connection = sqlite3.connect(database)

        self.connection.row_factory = sqlite3.Row

        self._create_schema()

    # -------------------------------------------------------

    def _create_schema(self):

        sql = """

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

        """

        self.connection.execute(sql)

        self.connection.commit()

    # -------------------------------------------------------

    def add(

        self,

        security: Security,

    ):

        sql = """

        INSERT OR REPLACE INTO securities(

            asset_id,

            canonical_symbol,

            name,

            exchange,

            currency,

            asset_type,

            yahoo,

            fmp,

            alpha_vantage,

            polygon,

            finnhub,

            isin,

            figi

        )

        VALUES(

            ?,?,?,?,?,?,?,?,?,?,?,?,?

        )

        """

        self.connection.execute(

            sql,

            (

                security.asset_id,

                security.canonical_symbol,

                security.name,

                security.exchange,

                security.currency,

                security.asset_type,

                security.yahoo,

                security.fmp,

                security.alpha_vantage,

                security.polygon,

                security.finnhub,

                security.isin,

                security.figi,

            ),

        )

        self.connection.commit()

    # -------------------------------------------------------

    def get(

        self,

        symbol: str,

    ) -> Security | None:

        sql = """

        SELECT *

        FROM securities

        WHERE

            canonical_symbol=?

            OR yahoo=?

            OR fmp=?

            OR polygon=?

            OR alpha_vantage=?

            OR finnhub=?

            OR isin=?

            OR figi=?

        """

        row = self.connection.execute(

            sql,

            (

                symbol,

                symbol,

                symbol,

                symbol,

                symbol,

                symbol,

                symbol,

                symbol,

            ),

        ).fetchone()

        if row is None:

            return None

        return Security(

            asset_id=row["asset_id"],

            canonical_symbol=row["canonical_symbol"],

            name=row["name"],

            exchange=row["exchange"],

            currency=row["currency"],

            asset_type=row["asset_type"],

            yahoo=row["yahoo"],

            fmp=row["fmp"],

            alpha_vantage=row["alpha_vantage"],

            polygon=row["polygon"],

            finnhub=row["finnhub"],

            isin=row["isin"],

            figi=row["figi"],

        )

    # -------------------------------------------------------

    def provider_symbol(

        self,

        symbol: str,

        provider: str,

    ) -> str:

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

    # -------------------------------------------------------

    def exists(

        self,

        symbol: str,

    ) -> bool:

        return self.get(symbol) is not None

    # -------------------------------------------------------

    def list_all(self):

        sql = """

        SELECT *

        FROM securities

        ORDER BY canonical_symbol

        """

        rows = self.connection.execute(sql)

        return [dict(r) for r in rows]

    # -------------------------------------------------------

    def delete(

        self,

        symbol: str,

    ):

        sql = """

        DELETE

        FROM securities

        WHERE canonical_symbol=?

        """

        self.connection.execute(

            sql,

            (symbol,),

        )

        self.connection.commit()

    # -------------------------------------------------------

    def close(self):

        self.connection.close()


# ============================================================
# EXAMPLE
# ============================================================

if __name__ == "__main__":

    sm = SecurityMaster()

    sm.add(

        Security(

            asset_id="AST000001",

            canonical_symbol="FMTY14.MX",

            name="Fibra Mty",

            exchange="BMV",

            currency="MXN",

            asset_type="REIT",

            yahoo="FMTY14.MX",

            fmp="FMTY14",

            polygon="FMTY14",

            isin="MXCFMT000001",

        )

    )

    print(sm.exists("FMTY14.MX"))

    print(sm.provider_symbol("FMTY14.MX", "yahoo"))

    print(sm.provider_symbol("FMTY14.MX", "fmp"))

    print(sm.provider_symbol("FMTY14.MX", "polygon"))

    print(sm.get("MXCFMT000001"))

    sm.close()