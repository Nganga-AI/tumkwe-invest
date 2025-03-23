"""
Tests for Yahoo Finance data collector.
"""

import datetime
import unittest
from unittest.mock import MagicMock, PropertyMock, patch

import pandas as pd

from tumkwe_invest.datacollection.collectors.yahoo_finance import (
    get_company_profile,
    get_financial_statements,
    get_stock_data,
)


class TestYahooFinance(unittest.TestCase):

    def test_get_stock_data(self):
        # Setup mock
        with patch("yfinance.download") as mock_yf_download:
            mock_data = MagicMock()
            mock_data.iterrows.return_value = [
                (
                    datetime.datetime(2023, 1, 1),
                    {
                        "Open": 100.0,
                        "High": 105.0,
                        "Low": 98.0,
                        "Close": 102.0,
                        "Volume": 1000000,
                        "Adj Close": 102.0,
                    },
                ),
                (
                    datetime.datetime(2023, 1, 2),
                    {
                        "Open": 102.0,
                        "High": 106.0,
                        "Low": 101.0,
                        "Close": 105.0,
                        "Volume": 1200000,
                        "Adj Close": 105.0,
                    },
                ),
            ]
            mock_yf_download.return_value = mock_data

            # Call function
            result = get_stock_data("AAPL", "2023-01-01", "2023-01-02")

            # Assertions
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0].symbol, "AAPL")
            self.assertEqual(result[0].open, 100.0)
            self.assertEqual(result[0].high, 105.0)
            self.assertEqual(result[0].low, 98.0)
            self.assertEqual(result[0].close, 102.0)
            self.assertEqual(result[0].volume, 1000000)
            self.assertEqual(result[0].adjusted_close, 102.0)
            self.assertEqual(result[0].source, "yahoo_finance")

            # Check that yf.download was called with the right parameters
            mock_yf_download.assert_called_once_with(
                "AAPL", start="2023-01-01", end="2023-01-02"
            )

    def test_get_company_profile(self):
        # Setup mock
        with patch("yfinance.Ticker") as mock:
            ticker_instance = MagicMock()
            mock.return_value = ticker_instance

            ticker_instance.info = {
                "longName": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "longBusinessSummary": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
                "website": "https://www.apple.com",
                "fullTimeEmployees": 154000,
                "country": "United States",
            }

            # Call function
            result = get_company_profile("AAPL")

            # Assertions
            self.assertIsNotNone(result)
            self.assertEqual(result.symbol, "AAPL")
            self.assertEqual(result.name, "Apple Inc.")
            self.assertEqual(result.sector, "Technology")
            self.assertEqual(result.industry, "Consumer Electronics")
            self.assertEqual(
                result.description,
                "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
            )
            self.assertEqual(result.website, "https://www.apple.com")
            self.assertEqual(result.employees, 154000)
            self.assertEqual(result.country, "United States")
            self.assertEqual(result.source, "yahoo_finance")

    def test_get_company_profile_error(self):
        # Setup mock to raise an exception when accessing a dictionary key
        with patch("yfinance.Ticker") as mock_ticker:
            ticker_instance = MagicMock()
            mock_ticker.return_value = ticker_instance

            # Mock `info` as a property that raises an exception
            type(ticker_instance).info = PropertyMock(
                side_effect=Exception("API Error")
            )

            # Call function
            result = get_company_profile("AAPL")

            # Assertions
            self.assertIsNone(result)

    def test_get_financial_statements(self):
        # Mock the Ticker object
        with patch("yfinance.Ticker") as mock_ticker:
            ticker_instance = MagicMock()
            mock_ticker.return_value = ticker_instance

            # Mock financial statement data
            mock_date = "2022-12-31"  # Ensure it's a string, as used in `columns`

            # Create pandas DataFrames to simulate Yahoo Finance data structure
            income_data = pd.DataFrame(
                {mock_date: [100000000, 50000000, 50000000]},
                index=["Revenue", "CostOfRevenue", "GrossProfit"],
            )
            ticker_instance.income_stmt = income_data

            balance_data = pd.DataFrame(
                {mock_date: [200000000, 100000000, 100000000]},
                index=["TotalAssets", "TotalLiabilities", "StockholdersEquity"],
            )
            ticker_instance.balance_sheet = balance_data

            cashflow_data = pd.DataFrame(
                {mock_date: [30000000, -10000000, -5000000]},
                index=["OperatingCashFlow", "InvestingCashFlow", "FinancingCashFlow"],
            )
            ticker_instance.cashflow = cashflow_data

            # Call function
            result = get_financial_statements("AAPL")

            # Assertions
            self.assertEqual(len(result), 3)
            self.assertIn("income_statement", result)
            self.assertIn("balance_sheet", result)
            self.assertIn("cash_flow", result)

            # Verify income statement
            self.assertEqual(len(result["income_statement"]), 1)
            self.assertEqual(result["income_statement"][0].symbol, "AAPL")
            self.assertEqual(
                result["income_statement"][0].statement_type, "income_statement"
            )
            self.assertEqual(result["income_statement"][0].period, "annual")
            self.assertEqual(result["income_statement"][0].date, mock_date)
            self.assertEqual(result["income_statement"][0].data["Revenue"], 100000000)

            # Verify balance sheet
            self.assertEqual(len(result["balance_sheet"]), 1)
            self.assertEqual(result["balance_sheet"][0].data["TotalAssets"], 200000000)

            # Verify cash flow statement
            self.assertEqual(len(result["cash_flow"]), 1)
            self.assertEqual(result["cash_flow"][0].data["OperatingCashFlow"], 30000000)

    def test_get_financial_statements_error(self):
        # Setup mocks to raise exceptions
        with patch("yfinance.Ticker") as mock:
            ticker_instance = MagicMock()
            mock.return_value = ticker_instance

            ticker_instance.income_stmt.__getitem__.side_effect = Exception("API Error")
            ticker_instance.balance_sheet.__getitem__.side_effect = Exception(
                "API Error"
            )
            ticker_instance.cashflow.__getitem__.side_effect = Exception("API Error")

            # Call function
            result = get_financial_statements("AAPL")

            # Assertions
            self.assertEqual(len(result), 3)
            self.assertEqual(len(result["income_statement"]), 0)
            self.assertEqual(len(result["balance_sheet"]), 0)
            self.assertEqual(len(result["cash_flow"]), 0)


if __name__ == "__main__":
    unittest.main()
