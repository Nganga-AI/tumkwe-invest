import yfinance as yf
from langchain_core.tools import tool


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
def get_stock_balance_sheet(ticker: str, freq: str = "yearly") -> dict:
    """
    Get the balance sheet data for a company.

    Args:
        ticker: Stock ticker symbol
        freq: Data frequency - "yearly", "quarterly", or "trailing"

    Returns:
        Balance sheet data as dictionary
    """
    return yf.Ticker(ticker).get_balance_sheet(as_dict=True, pretty=True, freq=freq)


@tool
def get_stock_income_statement(ticker: str, freq: str = "yearly") -> dict:
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
def get_stock_cash_flow(ticker: str, freq: str = "yearly") -> dict:
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
def get_stock_recommendations(ticker: str) -> dict:
    """
    Get analyst recommendations for a stock.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Analyst recommendations with strongBuy, buy, hold, sell, strongSell counts
    """
    return yf.Ticker(ticker).get_recommendations(as_dict=True)


tools = [
    get_stock_info,
    get_stock_price_history,
    get_stock_balance_sheet,
    get_stock_income_statement,
    get_stock_cash_flow,
    get_stock_recommendations,
]

TOOL_DESCRIPTION = """
Handles queries about current stocks, financial data, and market insights.
It provides functions to retrieve company info, historical prices, financial statements, and analysis data using yfinance.
"""
