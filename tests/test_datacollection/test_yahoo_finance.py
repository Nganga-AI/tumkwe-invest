"""
Tests for the Yahoo Finance collector.
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

import pandas as pd

from tumkwe_invest.datacollection.collectors.yahoo_finance import (
    get_stock_data, get_company_profile, get_financial_statements
)


class TestYahooFinance(unittest.TestCase):
    """Tests for the Yahoo Finance collector."""
    
    @patch('datacollection.collectors.yahoo_finance.yf.download')
    def test_get_stock_data(self, mock_download):
        """Test stock data collection."""
        # Create mock data
        mock_data = pd.DataFrame({
            'Open': [150.0, 151.0],
            'High': [155.0, 156.0],
            'Low': [148.0, 149.0],
            'Close': [153.0, 154.0],
            'Adj Close': [152.5, 153.5],
            'Volume': [10000000, 11000000]
        }, index=[
            pd.Timestamp('2023-01-01'),
            pd.Timestamp('2023-01-02')
        ])
        
        # Configure the mock
        mock_download.return_value = mock_data
        
        # Call the function
        results = get_stock_data("AAPL", "2023-01-01", "2023-01-02")
        
        # Validate the results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].symbol, "AAPL")
        self.assertEqual(results[0].open, 150.0)
        self.assertEqual(results[0].high, 155.0)
        self.assertEqual(results[0].low, 148.0)
        self.assertEqual(results[0].close, 153.0)
        self.assertEqual(results[0].adjusted_close, 152.5)
        self.assertEqual(results[0].volume, 10000000)
    
    @patch('datacollection.collectors.yahoo_finance.yf.Ticker')
    def test_get_company_profile(self, mock_ticker_class):
        """Test company profile collection."""
        # Create mock ticker
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        
        # Configure the mock ticker info
        mock_ticker.info = {
            'longName': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'longBusinessSummary': 'Apple Inc. designs, manufactures, and markets smartphones...',
            'website': 'https://www.apple.com',
            'fullTimeEmployees': 154000,
            'country': 'United States'
        }
        
        # Call the function
        result = get_company_profile("AAPL")
        
        # Validate the result
        self.assertEqual(result.symbol, "AAPL")
        self.assertEqual(result.name, "Apple Inc.")
        self.assertEqual(result.sector, "Technology")
        self.assertEqual(result.industry, "Consumer Electronics")
        self.assertEqual(result.website, "https://www.apple.com")
        self.assertEqual(result.employees, 154000)
        self.assertEqual(result.country, "United States")
    
    @patch('datacollection.collectors.yahoo_finance.yf.Ticker')
    def test_get_financial_statements(self, mock_ticker_class):
        """Test financial statements collection."""
        # Create mock ticker
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        
        # Create mock financial data
        mock_date = pd.Timestamp('2022-12-31')
        
        # Mock income statement
        mock_income = pd.DataFrame({
            mock_date: {
                'Total Revenue': 100000000.0,
                'Net Income': 20000000.0
            }
        })
        
        # Mock balance sheet
        mock_balance = pd.DataFrame({
            mock_date: {
                'Total Assets': 350000000.0,
                'Total Liabilities': 200000000.0,
                'Total Equity': 150000000.0
            }
        })
        
        # Mock cash flow
        mock_cashflow = pd.DataFrame({
            mock_date: {
                'Operating Cash Flow': 30000000.0,
                'Capital Expenditure': -5000000.0
            }
        })
        
        # Configure the mocks
        mock_ticker.income_stmt = mock_income
        mock_ticker.balance_sheet = mock_balance
        mock_ticker.cashflow = mock_cashflow
        
        # Call the function
        results = get_financial_statements("AAPL")
        
        # Validate the results
        self.assertIn('income_statement', results)
        self.assertIn('balance_sheet', results)
        self.assertIn('cash_flow', results)
        
        # Check income statement data
        income_statements = results['income_statement']
        self.assertEqual(len(income_statements), 1)
        self.assertEqual(income_statements[0].symbol, "AAPL")
        self.assertEqual(income_statements[0].statement_type, "income_statement")
        self.assertEqual(income_statements[0].period, "annual")
        self.assertEqual(income_statements[0].data['Total Revenue'], 100000000.0)
        self.assertEqual(income_statements[0].data['Net Income'], 20000000.0)
        
        # Check balance sheet data
        balance_sheets = results['balance_sheet']
        self.assertEqual(len(balance_sheets), 1)
        self.assertEqual(balance_sheets[0].symbol, "AAPL")
        self.assertEqual(balance_sheets[0].statement_type, "balance_sheet")
        self.assertEqual(balance_sheets[0].data['Total Assets'], 350000000.0)
        self.assertEqual(balance_sheets[0].data['Total Liabilities'], 200000000.0)
        self.assertEqual(balance_sheets[0].data['Total Equity'], 150000000.0)
        
        # Check cash flow data
        cash_flows = results['cash_flow']
        self.assertEqual(len(cash_flows), 1)
        self.assertEqual(cash_flows[0].symbol, "AAPL")
        self.assertEqual(cash_flows[0].statement_type, "cash_flow")
        self.assertEqual(cash_flows[0].data['Operating Cash Flow'], 30000000.0)
        self.assertEqual(cash_flows[0].data['Capital Expenditure'], -5000000.0)


if __name__ == "__main__":
    unittest.main()
