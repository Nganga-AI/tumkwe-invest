"""
Data models for storing collected financial information.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class StatementType(Enum):
    """Types of financial statements"""

    INCOME = "income_statement"
    BALANCE = "balance_sheet"
    CASH_FLOW = "cash_flow"
    KEY_METRICS = "key_metrics"
    RATIOS = "financial_ratios"


class Period(Enum):
    """Reporting periods for financial data"""

    ANNUAL = "annual"
    QUARTERLY = "quarterly"
    TTM = "trailing"  # Trailing twelve months


@dataclass
class DataSource:
    symbol: str
    source: str


@dataclass
class StockPrice(DataSource):
    """Stock price information for a given symbol and date."""

    close: Optional[float] = None  # Closing price, may be missing
    high: Optional[float] = None  # Highest price in period
    low: Optional[float] = None  # Lowest price in period
    open: Optional[float] = None  # Opening price
    stock_splits: float = 0.0  # Stock split ratio, default to no split
    volume: Optional[float] = None  # Trading volume
    date: Optional[datetime] = None  # Date of price data

    def __post_init__(self):
        # Ensure non-negative values where applicable
        for field_name in ["close", "high", "low", "open", "volume"]:
            value = getattr(self, field_name)
            if value is not None and value < 0:
                setattr(self, field_name, None)


@dataclass
class FinancialStatement(DataSource):
    """Financial statement data"""

    statement_type: StatementType = field(default=StatementType.INCOME)
    period: Period = field(default=Period.ANNUAL)
    date: Optional[datetime] = None
    data: Dict[str, float] = field(default_factory=dict)


@dataclass
class CompanyProfile(DataSource):
    """Company profile information"""

    name: str
    sector: str
    industry: str
    description: str
    website: Optional[str] = None
    employees: Optional[int] = None
    country: Optional[str] = None
    exchange: Optional[str] = None
    market_cap: Optional[float] = None
    ipo_date: Optional[datetime] = None
    logo_url: Optional[str] = None
    ceo: Optional[str] = None
    address: Optional[str] = None


@dataclass
class KeyMetrics(DataSource):
    """Key financial metrics for a company"""

    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    eps: Optional[float] = None
    market_cap: Optional[float] = None
    debt_to_equity: Optional[float] = None
    return_on_equity: Optional[float] = None
    return_on_assets: Optional[float] = None
    profit_margin: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    date: Optional[datetime] = None

    def __post_init__(self):
        float_fields = [
            "pe_ratio",
            "pb_ratio",
            "dividend_yield",
            "eps",
            "market_cap",
            "debt_to_equity",
            "return_on_equity",
            "return_on_assets",
            "profit_margin",
            "current_ratio",
            "quick_ratio",
        ]
        for field_name in float_fields:
            value = getattr(self, field_name)
            if isinstance(value, str):
                try:
                    setattr(self, field_name, float(value))
                except ValueError:
                    setattr(self, field_name, None)


@dataclass
class News:
    company_symbol: str
    title: str
    publication: str
    date: datetime
    url: str
    summary: str
    content: Optional[str] = None


@dataclass
class NewsArticle(News):
    """News article related to a company"""

    sentiment: Optional[float] = None  # Typically -1 to 1
    relevance_score: Optional[float] = None  # Typically 0 to 1
    categories: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.sentiment is not None:
            self.sentiment = max(-1.0, min(1.0, self.sentiment))  # Clamp to [-1, 1]
        if self.relevance_score is not None:
            self.relevance_score = max(
                0.0, min(1.0, self.relevance_score)
            )  # Clamp to [0, 1]


@dataclass
class WarningResult:
    last_updated: datetime = field(default_factory=datetime.now)
    validation_warnings: List[str] = field(default_factory=list)
    is_valid: bool = True
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationReport:
    """Report on data validation results"""

    timestamp: datetime = field(default_factory=datetime.now)
    data_type: str = ""
    source: str = ""
    company_symbol: str = ""
    total_records: int = 0
    valid_records: int = 0
    issues: Dict[str, List[str]] = field(default_factory=dict)
    missing_fields: Set[str] = field(default_factory=set)
    outliers: Dict[str, List[Any]] = field(default_factory=dict)
