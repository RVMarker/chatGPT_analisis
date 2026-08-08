from enum import Enum

class Decision(Enum):
    BUY = "BUY"
    ACCUMULATE = "ACCUMULATE"
    HOLD = "HOLD"
    REDUCE = "REDUCE"
    SELL = "SELL"

class Provider(Enum):
    YAHOO = "Yahoo Finance"
    FMP = "Financial Modeling Prep"
    ALPHA_VANTAGE = "Alpha Vantage"
    POLYGON = "Polygon"
    FINNHUB = "Finnhub"

class AssetType(Enum):
    STOCK = "Stock"
    ETF = "ETF"
    REIT = "REIT"
    FIBRA = "FIBRA"
    CRYPTO = "Crypto"
    BOND = "Bond"
    INDEX = "Index"
    FOREX = "Forex"

class Currency(Enum):
    USD = "USD"
    MXN = "MXN"
    EUR = "EUR"
    GBP = "GBP"

class Exchange(Enum):
    NASDAQ = "NASDAQ"
    NYSE = "NYSE"
    BMV = "BMV"
    BIVA = "BIVA"
    CME = "CME"

class ReportFormat(Enum):
    HTML = "html"
    PDF = "pdf"
    DOCX = "docx"
    JSON = "json"

class ConfidenceLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"

class AnalysisStatus(Enum):
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    FAILED = "FAILED"
