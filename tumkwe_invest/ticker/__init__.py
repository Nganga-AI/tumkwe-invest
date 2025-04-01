from langchain_core.tools import tool
import yfinance as yf
from datetime import datetime
from loguru import logger


@tool
def get_stock_info(ticker: str) -> dict:
    """
    Get detailed information about a stock.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT)

    Returns:
        Dictionary containing comprehensive company information
    """
    return yf.Ticker(ticker).get_info()


@tool
def get_stock_price_history(
    ticker: str,
    period: str = "1mo",
    interval: str = "1d",
    start: str = None,
    end: str = None,
) -> dict:
    """
    Get historical price data for a stock.

    Args:
        ticker: Stock ticker symbol
        period: Time period to retrieve data for (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        start: Start date in YYYY-MM-DD format (optional)
        end: End date in YYYY-MM-DD format (optional)

    Returns:
        DataFrame with historical price data
    """
    return (
        yf.Ticker(ticker)
        .history(period=period, interval=interval, start=start, end=end)
        .to_dict()
    )


@tool
def get_stock_balance_sheet(
    ticker: str, freq: str = "yearly"
) -> dict:
    """
    Get the balance sheet data for a company.

    Args:
        ticker: Stock ticker symbol
        freq: Data frequency - "yearly", "quarterly", or "trailing"

    Returns:
        Balance sheet data as dictionary
    """
    return yf.Ticker(ticker).get_balance_sheet(
        as_dict=True, pretty=True, freq=freq
    )


@tool
def get_stock_income_statement(
    ticker: str, freq: str = "yearly"
) -> dict:
    """
    Get the income statement data for a company.

    Args:
        ticker: Stock ticker symbol
        freq: Data frequency - "yearly", "quarterly", or "trailing"

    Returns:
        Income statement data as dictionary
    """
    return yf.Ticker(ticker).get_income_stmt(as_dict=True, pretty=True, freq=freq)


@tool
def get_stock_cash_flow(
    ticker: str, freq: str = "yearly"
) -> dict:
    """
    Get the cash flow data for a company.

    Args:
        ticker: Stock ticker symbol
        freq: Data frequency - "yearly", "quarterly", or "trailing"

    Returns:
        Cash flow data as dictionary
    """
    return yf.Ticker(ticker).get_cash_flow(as_dict=True, pretty=True, freq=freq)


@tool
def get_stock_dividends(ticker: str, period: str = "max") -> dict:
    """
    Get dividend history for a stock.

    Args:
        ticker: Stock ticker symbol
        period: Time period to retrieve data for (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

    Returns:
        Series with dividend data converted to dict
    """
    return yf.Ticker(ticker).get_dividends(period=period).to_dict()


@tool
def get_stock_recommendations(ticker: str) -> dict:
    """
    Get analyst recommendations for a stock.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Analyst recommendations with strongBuy, buy, hold, sell, strongSell counts
    """
    return yf.Ticker(ticker).get_recommendations(as_dict=True)


@tool
def get_stock_analyst_price_targets(ticker: str) -> dict:
    """
    Get analyst price targets for a stock.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with current, low, high, mean, and median price targets
    """
    return yf.Ticker(ticker).get_analyst_price_targets()


@tool
def get_stock_earnings(ticker: str, freq: str = "yearly") -> dict:
    """
    Get earnings data for a company.

    Args:
        ticker: Stock ticker symbol
        freq: Data frequency - "yearly" or "quarterly"

    Returns:
        Earnings data as dictionary
    """
    return yf.Ticker(ticker).get_earnings(as_dict=True, freq=freq)


@tool
def get_stock_major_holders(ticker: str) -> dict:
    """
    Get information about major shareholders.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Information about major shareholders
    """
    return yf.Ticker(ticker).get_major_holders(as_dict=True)


@tool
def get_stock_institutional_holders(ticker: str) -> dict:
    """
    Get information about institutional shareholders.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Information about institutional shareholders
    """
    return yf.Ticker(ticker).get_institutional_holders(as_dict=True)


tools = [
    get_stock_info,
    get_stock_price_history,
    get_stock_balance_sheet,
    get_stock_income_statement,
    get_stock_cash_flow,
    get_stock_dividends,
    get_stock_recommendations,
    get_stock_analyst_price_targets,
    get_stock_earnings,
    get_stock_major_holders,
    get_stock_institutional_holders,
]
