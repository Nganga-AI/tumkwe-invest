"""
Tests for the financial metrics collector.
"""
import unittest
from unittest.mock import patch, MagicMock
import os
from datetime import datetime
import pandas as pd
import json

from datacollection.collectors.financial_metrics import (
    get_key_metrics_yf, get_alpha_vantage_metrics,
    get_comprehensive_metrics, get_quarterly_financial_data
)


class TestFinancialMetrics(unittest.TestCase):
    """Tests for the financial metrics collector."""
    
    @patch('datacollection.collectors.financial_metrics.yf.Ticker')
    def test_get_key_metrics_yf(self, mock_ticker_class):
        """Test getting key metrics from Yahoo Finance."""
        # Create mock ticker
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        
        # Configure the mock ticker info
        mock_ticker.info = {
            'trailingPE': 30.5,
            'priceToBook': 12.75,
            'dividendYield': 0.005,
            'trailingEps': 6.15,
            'marketCap': 2500000000000,
            'profitMargins': 0.25
        }
        
        # Mock balance sheet
        mock_date = pd.Timestamp('2022-12-31')
        mock_balance = pd.DataFrame({
            mock_date: {
                'Total Assets': 350000000000.0,
                'Total Liabilities Net Minority Interest': 200000000000.0,
                'Total Equity': 150000000000.0,
                'Current Assets': 100000000000.0,
                'Current Liabilities': 80000000000.0
            }
        })
        mock_ticker.balance_sheet = mock_balance
        
        # Mock income statement
        mock_income = pd.DataFrame({
            mock_date: {
                'Net Income': 30000000000.0
            }
        })
        mock_ticker.income_stmt = mock_income
        
        # Call the function
        result = get_key_metrics_yf("AAPL")
        
        # Validate result
        self.assertEqual(result.symbol, "AAPL")
        self.assertEqual(result.source, "yahoo_finance")
        self.assertEqual(result.pe_ratio, 30.5)
        self.assertEqual(result.pb_ratio, 12.75)
        self.assertEqual(result.dividend_yield, 0.005)
        self.assertEqual(result.eps, 6.15)
        self.assertEqual(result.market_cap, 2500000000000)
        self.assertEqual(result.profit_margin, 0.25)
        
        # Check calculated ratios
        self.assertAlmostEqual(result.debt_to_equity, 200000000000.0 / 150000000000.0)
        self.assertAlmostEqual(result.current_ratio, 100000000000.0 / 80000000000.0)
        self.assertAlmostEqual(result.return_on_equity, 30000000000.0 / 150000000000.0)
        self.assertAlmostEqual(result.return_on_assets, 30000000000.0 / 350000000000.0)
    
    @patch('datacollection.collectors.financial_metrics.requests.get')
    @patch('datacollection.collectors.financial_metrics.os.path.exists')
    @patch('datacollection.collectors.financial_metrics.open', new_callable=unittest.mock.mock_open)
    @patch('datacollection.collectors.financial_metrics.ALPHA_VANTAGE_API_KEY', 'dummy_key')
    @patch('datacollection.collectors.financial_metrics.time.sleep')
    def test_get_alpha_vantage_metrics(self, mock_sleep, mock_file, mock_exists, mock_get):
        """Test getting metrics from Alpha Vantage."""
        # Mock file does not exist
        mock_exists.return_value = False
        
        # Create mock response
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            'Symbol': 'AAPL',
            'Name': 'Apple Inc',
            'PERatio': '30.5',
            'PriceToBookRatio': '12.75',
            'DividendYield': '0.5',
            'EPS': '6.15',
            'ReturnOnEquityTTM': '0.20',
            'ReturnOnAssetsTTM': '0.10',
            'ProfitMargin': '0.25'
        }
        
        # Configure the mock
        mock_get.return_value = mock_response
        
        # Call the function
        result = get_alpha_vantage_metrics("AAPL")
        
        # Validate the result
        self.assertEqual(result['Symbol'], 'AAPL')
        self.assertEqual(result['PERatio'], '30.5')
        self.assertEqual(result['PriceToBookRatio'], '12.75')
        
        # Verify API call
        mock_get.assert_called_once()
        
        # Verify rate limiting
        mock_sleep.assert_called_once()
    
    @patch('datacollection.collectors.financial_metrics.get_key_metrics_yf')
    @patch('datacollection.collectors.financial_metrics.get_alpha_vantage_metrics')
    def test_get_comprehensive_metrics(self, mock_get_av, mock_get_yf):
        """Test getting comprehensive metrics from multiple sources."""
        # Set up mock for Yahoo Finance metrics
        yf_metrics = MagicMock()
        yf_metrics.symbol = "AAPL"
        yf_metrics.pe_ratio = 30.5
        yf_metrics.pb_ratio = 12.75
        yf_metrics.dividend_yield = None  # Deliberately set to None to test fallback
        yf_metrics.eps = 6.15
        yf_metrics.return_on_equity = None  # Deliberately set to None to test fallback
        mock_get_yf.return_value = yf_metrics
        
        # Set up mock for Alpha Vantage metrics
        mock_get_av.return_value = {
            'Symbol': 'AAPL',
            'DividendYield': '0.005',
            'ReturnOnEquityTTM': '0.20',
            'ReturnOnAssetsTTM': '0.10'
        }
        
        # Call the function
        result = get_comprehensive_metrics("AAPL")
        
        # Validate the result
        self.assertEqual(result.symbol, "AAPL")
        self.assertEqual(result.source, "combined")
        self.assertEqual(result.pe_ratio, 30.5)  # From Yahoo Finance
        self.assertEqual(result.pb_ratio, 12.75)  # From Yahoo Finance
        self.assertEqual(result.eps, 6.15)  # From Yahoo Finance
        self.assertEqual(result.dividend_yield, 0.005)  # From Alpha Vantage (fallback)
        self.assertEqual(result.return_on_equity, 0.20)  # From Alpha Vantage (fallback)
        self.assertEqual(result.return_on_assets, 0.10)  # From Alpha Vantage (fallback)
    
    @patch('datacollection.collectors.financial_metrics.yf.Ticker')
    def test_get_quarterly_financial_data(self, mock_ticker_class):
        """Test getting quarterly financial data."""
        # Create mock ticker
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        
        # Create mock quarterly data
        mock_date1 = pd.Timestamp('2022-03-31')
        mock_date2 = pd.Timestamp('2022-06-30')
        
        # Mock quarterly income statement
        mock_income_q = pd.DataFrame({
            mock_date1: {'Total Revenue': 97000000000.0, 'Net Income': 25000000000.0},
            mock_date2: {'Total Revenue': 83000000000.0, 'Net Income': 19000000000.0}
        })
        mock_ticker.quarterly_income_stmt = mock_income_q
        
        # Mock quarterly balance sheet
        mock_balance_q = pd.DataFrame({
            mock_date1: {'Total Assets': 340000000000.0, 'Total Equity': 140000000000.0},
            mock_date2: {'Total Assets': 350000000000.0, 'Total Equity': 150000000000.0}
        })
        mock_ticker.quarterly_balance_sheet = mock_balance_q
        
        # Mock quarterly cash flow
        mock_cashflow_q = pd.DataFrame({
            mock_date1: {'Operating Cash Flow': 28000000000.0, 'Capital Expenditure': -4000000000.0},
            mock_date2: {'Operating Cash Flow': 25000000000.0, 'Capital Expenditure': -5000000000.0}
        })
        mock_ticker.quarterly_cashflow = mock_cashflow_q
        
        # Call the function
        result = get_quarterly_financial_data("AAPL")
        
        # Validate the result
        self.assertIn('income_statement', result)
        self.assertIn('balance_sheet', result)
        self.assertIn('cash_flow', result)
        
        # Check income statement data
        income_statements = result['income_statement']
        self.assertEqual(len(income_statements), 2)
        self.assertEqual(income_statements[0].statement_type, "income_statement")
        self.assertEqual(income_statements[0].period, "quarterly")
        self.assertEqual(income_statements[0].data['Total Revenue'], 97000000000.0)
        self.assertEqual(income_statements[1].data['Net Income'], 19000000000.0)
        
        # Check balance sheet data
        balance_sheets = result['balance_sheet']
        self.assertEqual(len(balance_sheets), 2)
        self.assertEqual(balance_sheets[0].statement_type, "balance_sheet")
        self.assertEqual(balance_sheets[0].data['Total Assets'], 340000000000.0)
        self.assertEqual(balance_sheets[1].data['Total Equity'], 150000000000.0)
        
        # Check cash flow data
        cash_flows = result['cash_flow']
        self.assertEqual(len(cash_flows), 2)
        self.assertEqual(cash_flows[0].statement_type, "cash_flow")
        self.assertEqual(cash_flows[0].data['Operating Cash Flow'], 28000000000.0)
        self.assertEqual(cash_flows[1].data['Capital Expenditure'], -5000000000.0)


if __name__ == "__main__":
    unittest.main()
