"""
Collector for comprehensive financial metrics.
"""
import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import json
from typing import Dict, List, Optional, Any

from ..models import KeyMetrics, FinancialStatement
from ..config import ALPHA_VANTAGE_API_KEY, FINNHUB_API_KEY, API_RATE_LIMITS, CACHE_DIRECTORY

# Create cache directory
os.makedirs(os.path.join(CACHE_DIRECTORY, "financial_metrics"), exist_ok=True)


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
            pe_ratio=info.get('trailingPE'),
            pb_ratio=info.get('priceToBook'),
            dividend_yield=info.get('dividendYield'),
            eps=info.get('trailingEps'),
            market_cap=info.get('marketCap'),
            profit_margin=info.get('profitMargins')
        )
        
        # Try to get additional metrics from financial data
        try:
            balance_sheet = ticker.balance_sheet
            if not balance_sheet.empty:
                latest_date = balance_sheet.columns[0]
                total_assets = balance_sheet.loc['Total Assets'][latest_date]
                total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest'][latest_date]
                total_equity = balance_sheet.loc['Total Equity'][latest_date]
                current_assets = balance_sheet.loc['Current Assets'][latest_date]
                current_liabilities = balance_sheet.loc['Current Liabilities'][latest_date]
                
                # Calculate additional ratios
                metrics.debt_to_equity = total_liabilities / total_equity if total_equity else None
                metrics.current_ratio = current_assets / current_liabilities if current_liabilities else None
                
                # Get income statement for ROE and ROA
                income_stmt = ticker.income_stmt
                if not income_stmt.empty:
                    net_income = income_stmt.loc['Net Income'][latest_date]
                    metrics.return_on_equity = net_income / total_equity if total_equity else None
                    metrics.return_on_assets = net_income / total_assets if total_assets else None
        except Exception as e:
            print(f"Could not compute all metrics for {symbol}: {e}")
            
        return metrics
    
    except Exception as e:
        print(f"Error fetching metrics for {symbol}: {e}")
        return None


def get_alpha_vantage_metrics(symbol: str) -> Dict[str, Any]:
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
    
    cache_file = os.path.join(CACHE_DIRECTORY, "financial_metrics", f"{symbol}_alphavantage.json")
    
    # Try to get from cache if less than a day old
    if os.path.exists(cache_file):
        file_modified_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - file_modified_time < timedelta(days=1):
            with open(cache_file, 'r') as f:
                return json.load(f)
    
    try:
        # Respect rate limits
        time.sleep(12)  # Alpha Vantage free tier allows 5 calls per minute
        
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Cache the results
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=4)
        
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
    metrics = get_key_metrics_yf(symbol)
    
    if not metrics:
        metrics = KeyMetrics(
            symbol=symbol,
            source="combined",
            date=datetime.now()
        )
    else:
        metrics.source = "combined"
    
    # Add Alpha Vantage data if available
    try:
        av_data = get_alpha_vantage_metrics(symbol)
        
        if av_data:
            # Update metrics with Alpha Vantage data if previously None
            if metrics.pe_ratio is None:
                metrics.pe_ratio = float(av_data.get('PERatio', '0')) or None
            
            if metrics.pb_ratio is None:
                metrics.pb_ratio = float(av_data.get('PriceToBookRatio', '0')) or None
                
            if metrics.eps is None:
                metrics.eps = float(av_data.get('EPS', '0')) or None
                
            if metrics.profit_margin is None:
                metrics.profit_margin = float(av_data.get('ProfitMargin', '0')) or None
                
            # Add any missing metrics
            if metrics.dividend_yield is None and 'DividendYield' in av_data:
                metrics.dividend_yield = float(av_data.get('DividendYield', '0')) or None
                
            if metrics.return_on_equity is None and 'ReturnOnEquityTTM' in av_data:
                metrics.return_on_equity = float(av_data.get('ReturnOnEquityTTM', '0')) or None
                
            if metrics.return_on_assets is None and 'ReturnOnAssetsTTM' in av_data:
                metrics.return_on_assets = float(av_data.get('ReturnOnAssetsTTM', '0')) or None
    
    except Exception as e:
        print(f"Error combining Alpha Vantage metrics for {symbol}: {e}")
        
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
    
    result = {
        'income_statement': [],
        'balance_sheet': [],
        'cash_flow': []
    }
    
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
                fiscal_quarter=date_col.month // 3 + (1 if date_col.month % 3 > 0 else 0),
                fiscal_year=date_col.year
            )
            result['income_statement'].append(statement)
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
                fiscal_quarter=date_col.month // 3 + (1 if date_col.month % 3 > 0 else 0),
                fiscal_year=date_col.year
            )
            result['balance_sheet'].append(statement)
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
                fiscal_quarter=date_col.month // 3 + (1 if date_col.month % 3 > 0 else 0),
                fiscal_year=date_col.year
            )
            result['cash_flow'].append(statement)
    except Exception as e:
        print(f"Error fetching quarterly cash flow for {symbol}: {e}")
    
    return result
