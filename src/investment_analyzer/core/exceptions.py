class InvestmentAnalyzerError(Exception):
    """Base exception."""


class ProviderError(InvestmentAnalyzerError):
    """Provider failed."""


class SymbolNotFoundError(InvestmentAnalyzerError):
    """Ticker not found."""


class InvalidDataError(InvestmentAnalyzerError):
    """Invalid data."""


class ConfigurationError(InvestmentAnalyzerError):
    """Configuration error."""


class CacheError(InvestmentAnalyzerError):
    """Cache error."""


class DatabaseError(InvestmentAnalyzerError):
    """Database error."""


class AnalysisError(InvestmentAnalyzerError):
    """Analysis error."""