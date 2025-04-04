import yfinance as yf
from langchain_core.tools import tool


@tool(parse_docstring=True)
def get_stock_info(ticker: str) -> dict:
    """
    Get detailed information about a stock.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT). Use standard market symbols.

    Returns:
        Dictionary containing comprehensive company information including profile, financials, and metrics.
    """
    return yf.Ticker(ticker).get_info()


@tool(parse_docstring=True)
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
        ticker: Stock ticker symbol. Use standard market symbols.
        period: Time period to retrieve data for. Options include: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.
        interval: Data interval for price points. Options include: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo.
        start: Start date in YYYY-MM-DD format (optional). Used instead of period if specified.
        end: End date in YYYY-MM-DD format (optional). Defaults to today if not specified.

    Returns:
        DataFrame with historical price data including open, high, low, close, and volume information.
    """
    return (
        yf.Ticker(ticker)
        .history(period=period, interval=interval, start=start, end=end)
        .to_dict()
    )


@tool(parse_docstring=True)
def get_stock_balance_sheet(ticker: str, freq: str = "yearly") -> dict:
    """
    Get the balance sheet data for a company.

    Args:
        ticker: Stock ticker symbol. Use standard market symbols.
        freq: Data frequency. Options include: "yearly", "quarterly", or "trailing".

    Returns:
        Balance sheet data as dictionary containing assets, liabilities, and equity information.
    """
    return yf.Ticker(ticker).get_balance_sheet(as_dict=True, pretty=True, freq=freq)


@tool(parse_docstring=True)
def get_stock_income_statement(ticker: str, freq: str = "yearly") -> dict:
    """
    Get the income statement data for a company.

    Args:
        ticker: Stock ticker symbol. Use standard market symbols.
        freq: Data frequency. Options include: "yearly", "quarterly", or "trailing".

    Returns:
        Income statement data as dictionary containing revenue, expenses, and profit information.
    """
    return yf.Ticker(ticker).get_income_stmt(as_dict=True, pretty=True, freq=freq)


@tool(parse_docstring=True)
def get_stock_cash_flow(ticker: str, freq: str = "yearly") -> dict:
    """
    Get the cash flow data for a company.

    Args:
        ticker: Stock ticker symbol. Use standard market symbols.
        freq: Data frequency. Options include: "yearly", "quarterly", or "trailing".

    Returns:
        Cash flow data as dictionary showing operating, investing, and financing activities.
    """
    return yf.Ticker(ticker).get_cash_flow(as_dict=True, pretty=True, freq=freq)


@tool(parse_docstring=True)
def get_stock_recommendations(ticker: str) -> dict:
    """
    Get analyst recommendations for a stock.

    Args:
        ticker: Stock ticker symbol. Use standard market symbols.

    Returns:
        Analyst recommendations with strongBuy, buy, hold, sell, strongSell counts and recommendation trends.
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
