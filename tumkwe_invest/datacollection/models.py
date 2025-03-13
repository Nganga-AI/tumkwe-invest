"""
Data models for storing collected financial information.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set


@dataclass
class FinancialData:
    """Base class for financial data"""

    symbol: str
    source: str
    last_updated: datetime = field(default_factory=datetime.now)
    validation_warnings: List[str] = field(default_factory=list)
    is_valid: bool = True


@dataclass
class StockPrice(FinancialData):
    """Stock price information"""

    date: datetime = field(default_factory=datetime.now)
    open: float = field()
    high: float = field()
    low: float = field()
    close: float = field()
    volume: int = field()
    adjusted_close: Optional[float] = None


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
    TTM = "ttm"  # Trailing twelve months


@dataclass
class FinancialStatement(FinancialData):
    """Financial statement data"""

    statement_type: str = field()  # income_statement, balance_sheet, cash_flow
    period: str = field()  # annual, quarterly
    date: datetime = field(default_factory=datetime.now)
    data: Dict[str, float] = field()
    currency: str = "USD"
    fiscal_year: Optional[int] = None
    fiscal_quarter: Optional[int] = None


@dataclass
class CompanyProfile(FinancialData):
    """Company profile information"""

    name: str = field()
    sector: str = field()
    industry: str = field()
    description: str = field()
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
class KeyMetrics(FinancialData):
    """Key financial metrics for a company"""

    date: datetime = field(default_factory=datetime.now)
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


@dataclass
class NewsArticle:
    """News article related to a company"""

    company_symbol: str
    title: str
    publication: str
    date: datetime
    url: str
    summary: str
    content: Optional[str] = None
    sentiment: Optional[float] = None
    relevance_score: Optional[float] = None
    categories: List[str] = field(default_factory=list)


@dataclass
class SECFiling:
    """SEC filing information"""

    company_symbol: str
    filing_type: str  # 10-K, 10-Q, 8-K, etc.
    filing_date: datetime
    period_end_date: Optional[datetime] = field(default_factory=lambda: None)
    accession_number: Optional[str] = None
    url: Optional[str] = None
    document_text: Optional[str] = None
    extracted_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataCollectionTask:
    """Represents a data collection task for scheduling"""

    task_name: str
    data_type: str
    company_symbols: List[str]
    last_run: Optional[datetime] = field(default_factory=lambda: None)
    next_run: Optional[datetime] = field(default_factory=lambda: None)
    interval: timedelta = field(default_factory=lambda: timedelta(days=1))
    priority: int = 1  # Higher number = higher priority


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
