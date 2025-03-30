from langchain_core.tools import tool

from ..datacollection.collectors import (
    financial_metrics,
    news_collector,
    yahoo_news,
    yahoo_finance,
)
import json
from dataclasses import asdict, is_dataclass
import datetime

def to_json_dumps_data(obj):
    """
    Convert a dataclass object to a dictionary, handling datetime fields.
    """
    if is_dataclass(obj):
        obj_dict = asdict(obj)
        keys = list(obj_dict)
        for key in keys:
            value = obj_dict[key]
            if value is None:
                del obj_dict[key]
                continue
            if isinstance(value, (datetime.date, datetime.datetime)):
                obj_dict[key] = value.isoformat()
        return obj_dict
    if isinstance(obj, list):
        return [to_json_dumps_data(i) for i in obj]
    if isinstance(obj, dict):
        return {key: to_json_dumps_data(value) for key, value in obj.items()}
    return obj


@tool
def fetch_company_news(
    company_symbol: str = None,
    company_name: str = None,
    days: int = 5,
    max_articles: int = 25,
) -> list[news_collector.NewsArticle]:
    """
    Fetch news articles about a specific company.

    Args:
        company_symbol: Stock ticker symbol
        company_name: Company name for search
        days: Number of days to look back
        max_articles: Maximum number of articles to retrieve

    Returns:
        List of NewsArticle objects
    """
    if company_symbol: # Using Yahoo Finance API since it is free
        articles = yahoo_news.get_yahoo_finance_news(
            company_symbol, max_articles=max_articles
        )
    else:
        articles = news_collector.get_company_news(
            company_symbol, company_name, days, max_articles
        )
    return json.dumps(to_json_dumps_data(articles), indent=2)


@tool
def fetch_companies_stocks(
    tickers: list[str],
    start: str = None,
    end: str = None,
    period: str = "max",
    interval: str = "1d",
):
    """
    Fetch historical stock data from Yahoo Finance.

    Args:
        tickers : str, list
            List of tickers to download
        period : str
            Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            Either Use period parameter or use start and end
        interval : str
            Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            Intraday data cannot extend last 60 days
        start: str
            Download start date string (YYYY-MM-DD) or _datetime, inclusive.
            Default is 99 years ago
            E.g. for start="2020-01-01", the first data point will be on "2020-01-01"
        end: str
            Download end date string (YYYY-MM-DD) or _datetime, exclusive.
            Default is now
            E.g. for end="2023-01-01", the last data point will be on "2022-12-31"

    Returns:
        Dict of symbol, list of StockPrice objects
    """
    return to_json_dumps_data(
        yahoo_finance.get_stock_data(
            tickers,
            start=start,
            end=end,
            period=period,
            interval=interval,
        )
    )

@tool
def fetch_company_profile(ticker: str):
    """
    Fetch company profile information from Yahoo Finance.

    Args:
        ticker: The stock ticker symbol

    Returns:
        Dict with company profile information
    """
    return yahoo_finance.get_company_profile(ticker)

tools = [
    fetch_company_news, fetch_companies_stocks, fetch_company_profile
]