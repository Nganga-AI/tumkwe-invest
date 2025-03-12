"""
Data collector for Yahoo Finance.
"""
import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..models import StockPrice, CompanyProfile, FinancialStatement


def get_stock_data(symbol: str, start_date: str, end_date: str) -> List[StockPrice]:
    """
    Fetch historical stock data from Yahoo Finance.
    
    Args:
        symbol: The stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        List of StockPrice objects
    """
    stock_data = yf.download(symbol, start=start_date, end=end_date)
    
    result = []
    for index, row in stock_data.iterrows():
        price = StockPrice(
            symbol=symbol,
            source="yahoo_finance",
            date=index,
            open=row['Open'],
            high=row['High'],
            low=row['Low'],
            close=row['Close'],
            volume=row['Volume'],
            adjusted_close=row['Adj Close']
        )
        result.append(price)
    
    return result


def get_company_profile(symbol: str) -> Optional[CompanyProfile]:
    """
    Fetch company profile information.
    
    Args:
        symbol: The stock ticker symbol
        
    Returns:
        CompanyProfile object or None if data not available
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        profile = CompanyProfile(
            symbol=symbol,
            source="yahoo_finance",
            name=info.get('longName', ''),
            sector=info.get('sector', ''),
            industry=info.get('industry', ''),
            description=info.get('longBusinessSummary', ''),
            website=info.get('website', ''),
            employees=info.get('fullTimeEmployees'),
            country=info.get('country', '')
        )
        return profile
    except Exception as e:
        print(f"Error fetching company profile for {symbol}: {e}")
        return None


def get_financial_statements(symbol: str) -> Dict[str, List[FinancialStatement]]:
    """
    Fetch financial statements from Yahoo Finance.
    
    Args:
        symbol: The stock ticker symbol
        
    Returns:
        Dictionary with keys 'income_statement', 'balance_sheet', 'cash_flow'
        containing lists of FinancialStatement objects
    """
    ticker = yf.Ticker(symbol)
    
    result = {
        'income_statement': [],
        'balance_sheet': [],
        'cash_flow': []
    }
    
    # Income Statement
    try:
        income_stmt = ticker.income_stmt
        for date_col in income_stmt.columns:
            data = {row: income_stmt[date_col][row] for row in income_stmt.index}
            statement = FinancialStatement(
                symbol=symbol,
                source="yahoo_finance",
                statement_type="income_statement",
                period="annual",
                date=date_col,
                data=data
            )
            result['income_statement'].append(statement)
    except Exception as e:
        print(f"Error fetching income statement for {symbol}: {e}")
    
    # Balance Sheet
    try:
        balance = ticker.balance_sheet
        for date_col in balance.columns:
            data = {row: balance[date_col][row] for row in balance.index}
            statement = FinancialStatement(
                symbol=symbol,
                source="yahoo_finance",
                statement_type="balance_sheet",
                period="annual",
                date=date_col,
                data=data
            )
            result['balance_sheet'].append(statement)
    except Exception as e:
        print(f"Error fetching balance sheet for {symbol}: {e}")
    
    # Cash Flow
    try:
        cash_flow = ticker.cashflow
        for date_col in cash_flow.columns:
            data = {row: cash_flow[date_col][row] for row in cash_flow.index}
            statement = FinancialStatement(
                symbol=symbol,
                source="yahoo_finance",
                statement_type="cash_flow",
                period="annual",
                date=date_col,
                data=data
            )
            result['cash_flow'].append(statement)
    except Exception as e:
        print(f"Error fetching cash flow for {symbol}: {e}")
    
    return result
