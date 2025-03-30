"""
Data collector for Yahoo Finance.
"""

from collections import defaultdict
from typing import Dict, List, Optional, Union

import yfinance as yf

from ..models import CompanyProfile, FinancialStatement, StockPrice
from loguru import logger


def get_stock_data(
    tickers: Union[str, list[str]],
    start: str = None,
    end: str = None,
    period: str = "max",
    interval: str = "1d",
) -> Dict[str, List[StockPrice]]:
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
    stock_data = yf.download(
        tickers,
        start=start,
        end=end,
        period=period,
        interval=interval,
        progress=False,
        multi_level_index=True,
        actions=True,
    )

    results = defaultdict(list)
    extracted_tickers = set(j for _, j in stock_data.columns)
    for index, raw in stock_data.iterrows():
        # for symbol
        for symbol in extracted_tickers:
            results[symbol].append(
                StockPrice(
                    **{
                        "symbol": symbol,
                        "open": raw[("Open", symbol)],
                        "high": raw[("High", symbol)],
                        "low": raw[("Low", symbol)],
                        "close": raw[("Close", symbol)],
                        "volume": raw[("Volume", symbol)],
                        "stock_splits": raw[("Stock Splits", symbol)],
                        "date": index,
                    }
                )
            )
    return results


def get_company_profile(symbol: str) -> Optional[CompanyProfile]:
    """
    Fetch company profile information from Yahoo Finance.

    Args:
        symbol: The stock ticker symbol

    Returns:
        CompanyProfile object or None if data not available
    """
    try:
        ticker = yf.Ticker(symbol)
        return ticker.info
    except Exception as e:
        logger.error(f"Error fetching company profile for {symbol}: {e}")


def get_financial_statements(
    symbol: str, freq="yearly"
) -> Dict[str, List[FinancialStatement]]:
    """
    Fetch financial statements from Yahoo Finance.

    Args:
        symbol: The stock ticker symbol
        freq: str
            "yearly" or "quarterly" or "trailing"
            Default is "yearly"

    Returns:
        Dictionary with keys 'income_statement', 'balance_sheet', 'cash_flow'
        containing lists of FinancialStatement objects
    """
    ticker = yf.Ticker(symbol)

    result = {"income_statement": [], "balance_sheet": [], "cash_flow": []}

    # Income Statement
    try:
        income_stmt = ticker.get_income_stmt(pretty=True, freq=freq)
        for date_col in income_stmt.columns:
            statement = FinancialStatement(
                symbol=symbol,
                source="yahoo_finance",
                statement_type="income_statement",
                period=freq,
                date=date_col,
                data=income_stmt[date_col].to_dict(),
            )
            result["income_statement"].append(statement)
    except Exception as e:
        logger.error(f"Error fetching income statement for {symbol}: {e}")

    # Balance Sheet
    try:
        balance = ticker.get_balance_sheet(pretty=True, freq=freq)
        for date_col in balance.columns:
            statement = FinancialStatement(
                symbol=symbol,
                source="yahoo_finance",
                statement_type="balance_sheet",
                period=freq,
                date=date_col,
                data=balance[date_col].to_dict(),
            )
            result["balance_sheet"].append(statement)
    except Exception as e:
        logger.error(f"Error fetching balance sheet for {symbol}: {e}")

    # Cash Flow
    try:
        cash_flow = ticker.get_cash_flow(pretty=True, freq=freq)
        for date_col in cash_flow.columns:
            statement = FinancialStatement(
                symbol=symbol,
                source="yahoo_finance",
                statement_type="cash_flow",
                period=freq,
                date=date_col,
                data=cash_flow[date_col].to_dict(),
            )
            result["cash_flow"].append(statement)
    except Exception as e:
        logger.error(f"Error fetching cash flow for {symbol}: {e}")

    return result
