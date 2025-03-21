"""
Collector for comprehensive financial metrics.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
import yfinance as yf

from ..config import ALPHA_VANTAGE_API_KEY, CACHE_DIRECTORY
from ..models import FinancialStatement, KeyMetrics

# Create cache directory
os.makedirs(os.path.join(CACHE_DIRECTORY, "financial_metrics"), exist_ok=True)


def parse_float(value: Any) -> Optional[float]:
    return float(value) if value is not None else None


def get_key_metrics_yf(symbol: str) -> Optional[KeyMetrics]:
    """
    Get key financial metrics from Yahoo Finance.

    Args:
        symbol: Stock ticker symbol

    Returns:
        KeyMetrics object or None if data not available
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Calculate key metrics
        metrics = KeyMetrics(
            symbol=symbol,
            source="yahoo_finance",
            date=datetime.now(),
            pe_ratio=info.get("trailingPE"),
            pb_ratio=info.get("priceToBook"),
            dividend_yield=info.get("dividendYield"),
            eps=info.get("trailingEps"),
            market_cap=info.get("marketCap"),
            profit_margin=info.get("profitMargins"),
            debt_to_equity=info.get("debtToEquity"),
            return_on_equity=info.get("returnOnEquity"),
            return_on_assets=info.get("returnOnAssets"),
            current_ratio=info.get("currentRatio"),
            quick_ratio=info.get("quickRatio"),
        )

        return metrics

    except Exception as e:
        print(f"Error fetching metrics for {symbol}: {e}")
        return None


def get_alpha_vantage_metrics(symbol: str) -> Optional[KeyMetrics]:
    """
    Get fundamental metrics from Alpha Vantage.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dictionary with financial metrics
    """
    if not ALPHA_VANTAGE_API_KEY:
        print("Warning: ALPHA_VANTAGE_API_KEY not set. Cannot fetch metrics.")
        return {}

    try:
        # Respect rate limits
        # time.sleep(12)  # Alpha Vantage free tier allows 5 calls per minute

        url = "https://www.alphavantage.co/query"
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data: dict = response.json()

        data = KeyMetrics(
            symbol=symbol,
            source="alpha_vantage",
            date=datetime.now(),
            pe_ratio=data.get("PERatio"),
            pb_ratio=data.get("PriceToBookRatio"),
            dividend_yield=data.get("DividendYield"),
            eps=data.get("EPS"),
            profit_margin=data.get("ProfitMargin"),
            market_cap=data.get("MarketCapitalization"),
            debt_to_equity=data.get("DebtToEquity"),
            return_on_equity=data.get("ReturnOnEquityTTM"),
            return_on_assets=data.get("ReturnOnAssetsTTM"),
            current_ratio=data.get("CurrentRatio"),
            quick_ratio=data.get("QuickRatio"),
        )

        return data

    except Exception as e:
        print(f"Error fetching Alpha Vantage metrics for {symbol}: {e}")
        return {}


def get_comprehensive_metrics(symbol: str) -> Optional[KeyMetrics]:
    """
    Get comprehensive financial metrics combining multiple sources.

    Args:
        symbol: Stock ticker symbol

    Returns:
        KeyMetrics object or None if data not available
    """
    # Start with Yahoo Finance metrics
    yf_data = get_key_metrics_yf(symbol)
    av_data = get_alpha_vantage_metrics(symbol)

    # combine data
    metrics = KeyMetrics(
        symbol=symbol,
        source="combined",
        date=datetime.now(),
        pe_ratio=yf_data.pe_ratio or av_data.pe_ratio,
        pb_ratio=yf_data.pb_ratio or av_data.pb_ratio,
        dividend_yield=yf_data.dividend_yield or av_data.dividend_yield,
        eps=yf_data.eps or av_data.eps,
        market_cap=yf_data.market_cap or av_data.market_cap,
        profit_margin=yf_data.profit_margin or av_data.profit_margin,
        debt_to_equity=yf_data.debt_to_equity or av_data.debt_to_equity,
        return_on_equity=yf_data.return_on_equity or av_data.return_on_equity,
        return_on_assets=yf_data.return_on_assets or av_data.return_on_assets,
        current_ratio=yf_data.current_ratio or av_data.current_ratio,
        quick_ratio=yf_data.quick_ratio or av_data.quick_ratio,
    )

    return metrics


def get_quarterly_financial_data(symbol: str) -> Dict[str, List[FinancialStatement]]:
    """
    Get quarterly financial statements.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dictionary with quarterly financial statements
    """
    ticker = yf.Ticker(symbol)

    result = {"income_statement": [], "balance_sheet": [], "cash_flow": []}

    # Income Statement
    try:
        income_stmt_q = ticker.quarterly_income_stmt
        for date_col in income_stmt_q.columns:
            data = {row: income_stmt_q[date_col][row] for row in income_stmt_q.index}
            statement = FinancialStatement(
                symbol=symbol,
                source="yahoo_finance",
                statement_type="income_statement",
                period="quarterly",
                date=date_col,
                data=data,
                fiscal_quarter=date_col.month // 3
                + (1 if date_col.month % 3 > 0 else 0),
                fiscal_year=date_col.year,
            )
            result["income_statement"].append(statement)
    except Exception as e:
        print(f"Error fetching quarterly income statement for {symbol}: {e}")

    # Balance Sheet
    try:
        balance_q = ticker.quarterly_balance_sheet
        for date_col in balance_q.columns:
            data = {row: balance_q[date_col][row] for row in balance_q.index}
            statement = FinancialStatement(
                symbol=symbol,
                source="yahoo_finance",
                statement_type="balance_sheet",
                period="quarterly",
                date=date_col,
                data=data,
                fiscal_quarter=date_col.month // 3
                + (1 if date_col.month % 3 > 0 else 0),
                fiscal_year=date_col.year,
            )
            result["balance_sheet"].append(statement)
    except Exception as e:
        print(f"Error fetching quarterly balance sheet for {symbol}: {e}")

    # Cash Flow
    try:
        cash_flow_q = ticker.quarterly_cashflow
        for date_col in cash_flow_q.columns:
            data = {row: cash_flow_q[date_col][row] for row in cash_flow_q.index}
            statement = FinancialStatement(
                symbol=symbol,
                source="yahoo_finance",
                statement_type="cash_flow",
                period="quarterly",
                date=date_col,
                data=data,
                fiscal_quarter=date_col.month // 3
                + (1 if date_col.month % 3 > 0 else 0),
                fiscal_year=date_col.year,
            )
            result["cash_flow"].append(statement)
    except Exception as e:
        print(f"Error fetching quarterly cash flow for {symbol}: {e}")

    return result
