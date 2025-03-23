"""
Tests for financial metrics collectors.
"""

import datetime
import os
import unittest
from unittest.mock import MagicMock, patch

from tumkwe_invest.datacollection.collectors.financial_metrics import (
    get_alpha_vantage_metrics,
    get_comprehensive_metrics,
    get_key_metrics_yf,
    get_quarterly_financial_data,
)


class TestFinancialMetrics(unittest.TestCase):

    def setUp(self):
        # Save original env vars
        self.original_alpha_vantage_key = os.environ.get("ALPHA_VANTAGE_API_KEY", None)

    def tearDown(self):
        # Restore original env vars
        if self.original_alpha_vantage_key is not None:
            os.environ["ALPHA_VANTAGE_API_KEY"] = self.original_alpha_vantage_key
        elif "ALPHA_VANTAGE_API_KEY" in os.environ:
            del os.environ["ALPHA_VANTAGE_API_KEY"]

    def test_get_key_metrics_yf(self):
        # Setup mock ticker info
        with patch("yfinance.Ticker") as mock:
            ticker_instance = MagicMock()
            mock.return_value = ticker_instance

            ticker_instance.info = {
                "trailingPE": 25.6,
                "priceToBook": 12.3,
                "dividendYield": 0.015,
                "trailingEps": 5.61,
                "marketCap": 2500000000000,
                "profitMargins": 0.25,
                "debtToEquity": 1.5,
                "returnOnEquity": 0.35,
                "returnOnAssets": 0.15,
                "currentRatio": 1.8,
                "quickRatio": 1.5,
            }

            # Call function
            result = get_key_metrics_yf("AAPL")

            # Assertions
            self.assertIsNotNone(result)
            self.assertEqual(result.symbol, "AAPL")
            self.assertEqual(result.source, "yahoo_finance")
            self.assertIsInstance(result.date, datetime.datetime)
            self.assertEqual(result.pe_ratio, 25.6)
            self.assertEqual(result.pb_ratio, 12.3)
            self.assertEqual(result.dividend_yield, 0.015)
            self.assertEqual(result.eps, 5.61)
            self.assertEqual(result.market_cap, 2500000000000)
            self.assertEqual(result.profit_margin, 0.25)
            self.assertEqual(result.debt_to_equity, 1.5)
            self.assertEqual(result.return_on_equity, 0.35)
            self.assertEqual(result.return_on_assets, 0.15)
            self.assertEqual(result.current_ratio, 1.8)
            self.assertEqual(result.quick_ratio, 1.5)

    def test_get_key_metrics_yf_error(self):
        # Setup mock to raise exception
        with patch("yfinance.Ticker") as mock:
            ticker_instance = MagicMock()
            mock.return_value = ticker_instance

            ticker_instance.info.__getitem__.side_effect = Exception("API Error")

            # Call function
            result = get_key_metrics_yf("AAPL")

            # Should return None on error
            self.assertIsNone(result)

    def test_get_alpha_vantage_metrics(self):
        # Setup environment and mocks
        os.environ["ALPHA_VANTAGE_API_KEY"] = "fake-api-key"

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_get.return_value = mock_response

            # Mock the API response
            mock_response.json.return_value = {
                "Symbol": "AAPL",
                "PERatio": "25.6",
                "PriceToBookRatio": "12.3",
                "DividendYield": "1.5",
                "EPS": "5.61",
                "ProfitMargin": "0.25",
                "MarketCapitalization": "2500000000000",
                "DebtToEquity": "1.5",
                "ReturnOnEquityTTM": "0.35",
                "ReturnOnAssetsTTM": "0.15",
                "CurrentRatio": "1.8",
                "QuickRatio": "1.5",
            }

            # Call function
            result = get_alpha_vantage_metrics("AAPL")

            # Assertions
            self.assertIsNotNone(result)
            self.assertEqual(result.symbol, "AAPL")
            self.assertEqual(result.source, "alpha_vantage")
            self.assertIsInstance(result.date, datetime.datetime)
            # Alpha Vantage values are stored as strings, but KeyMetrics should convert them
            self.assertEqual(result.pe_ratio, "25.6")
            self.assertEqual(result.pb_ratio, "12.3")
            self.assertEqual(result.dividend_yield, "1.5")
            self.assertEqual(result.eps, "5.61")
            self.assertEqual(result.profit_margin, "0.25")
            self.assertEqual(result.market_cap, "2500000000000")
            self.assertEqual(result.debt_to_equity, "1.5")
            self.assertEqual(result.return_on_equity, "0.35")
            self.assertEqual(result.return_on_assets, "0.15")
            self.assertEqual(result.current_ratio, "1.8")
            self.assertEqual(result.quick_ratio, "1.5")

            # Check API call parameters
            mock_get.assert_called_once()
            args, kwargs = mock_get.call_args
            self.assertEqual(kwargs["params"]["function"], "OVERVIEW")
            self.assertEqual(kwargs["params"]["symbol"], "AAPL")
            self.assertEqual(kwargs["params"]["apikey"], "fake-api-key")

    def test_get_alpha_vantage_metrics_no_api_key(self):
        # Ensure API key is not set
        if "ALPHA_VANTAGE_API_KEY" in os.environ:
            del os.environ["ALPHA_VANTAGE_API_KEY"]

        # Call function
        result = get_alpha_vantage_metrics("AAPL")

        # Should return empty dict when API key is not available
        self.assertEqual(result, {})

    def test_get_comprehensive_metrics(self):
        # Setup mocks for both Yahoo Finance and Alpha Vantage
        os.environ["ALPHA_VANTAGE_API_KEY"] = "fake-api-key"

        # Mock YF Ticker
        with patch("yfinance.Ticker") as yf_mock:
            ticker_instance = MagicMock()
            yf_mock.return_value = ticker_instance

            # Mock YF response
            ticker_instance.info = {
                "trailingPE": 25.6,
                "priceToBook": 12.3,
                "dividendYield": None,  # Missing value to test fallback
                "trailingEps": 5.61,
                "marketCap": 2500000000000,
                "profitMargins": 0.25,
                "debtToEquity": None,  # Missing value to test fallback
                "returnOnEquity": 0.35,
                "returnOnAssets": 0.15,
                "currentRatio": 1.8,
                "quickRatio": 1.5,
            }

            # Mock Alpha Vantage API
            with patch("requests.get") as av_mock_get:
                mock_response = MagicMock()
                av_mock_get.return_value = mock_response

                # Mock Alpha Vantage response
                mock_response.json.return_value = {
                    "Symbol": "AAPL",
                    "PERatio": "26.0",
                    "PriceToBookRatio": "13.0",
                    "DividendYield": "1.5",  # Should be used as YF value is None
                    "EPS": "5.7",
                    "ProfitMargin": "0.26",
                    "MarketCapitalization": "2600000000000",
                    "DebtToEquity": "1.6",  # Should be used as YF value is None
                    "ReturnOnEquityTTM": "0.36",
                    "ReturnOnAssetsTTM": "0.16",
                    "CurrentRatio": "1.9",
                    "QuickRatio": "1.6",
                }

                # Call function
                result = get_comprehensive_metrics("AAPL")

                # Assertions
                self.assertIsNotNone(result)
                self.assertEqual(result.symbol, "AAPL")
                self.assertEqual(result.source, "combined")
                self.assertIsInstance(result.date, datetime.datetime)

                # Should use YF values where available
                self.assertEqual(result.pe_ratio, 25.6)
                self.assertEqual(result.pb_ratio, 12.3)
                self.assertEqual(result.eps, 5.61)
                self.assertEqual(result.market_cap, 2500000000000)
                self.assertEqual(result.profit_margin, 0.25)
                self.assertEqual(result.return_on_equity, 0.35)
                self.assertEqual(result.return_on_assets, 0.15)
                self.assertEqual(result.current_ratio, 1.8)
                self.assertEqual(result.quick_ratio, 1.5)

                # Should fall back to Alpha Vantage for missing YF values
                self.assertEqual(result.dividend_yield, "1.5")
                self.assertEqual(result.debt_to_equity, "1.6")

    def test_get_quarterly_financial_data(self):
        # Create mock date
        mock_date = datetime.datetime(2022, 3, 31)  # Q1

        with patch("yfinance.Ticker") as mock:
            ticker_instance = MagicMock()
            mock.return_value = ticker_instance

            # Create mock quarterly income statement
            income_stmt_q = MagicMock()
            income_stmt_q.columns = [mock_date]
            income_stmt_q[mock_date] = MagicMock()
            income_stmt_q.index = ["Revenue", "CostOfRevenue", "GrossProfit"]
            income_stmt_q[mock_date]["Revenue"] = 97000000000
            income_stmt_q[mock_date]["CostOfRevenue"] = 50000000000
            income_stmt_q[mock_date]["GrossProfit"] = 47000000000
            ticker_instance.quarterly_income_stmt = income_stmt_q

            # Create mock quarterly balance sheet
            balance_q = MagicMock()
            balance_q.columns = [mock_date]
            balance_q[mock_date] = MagicMock()
            balance_q.index = ["TotalAssets", "TotalLiabilities", "StockholdersEquity"]
            balance_q[mock_date]["TotalAssets"] = 350000000000
            balance_q[mock_date]["TotalLiabilities"] = 240000000000
            balance_q[mock_date]["StockholdersEquity"] = 110000000000
            ticker_instance.quarterly_balance_sheet = balance_q

            # Create mock quarterly cash flow
            cash_flow_q = MagicMock()
            cash_flow_q.columns = [mock_date]
            cash_flow_q[mock_date] = MagicMock()
            cash_flow_q.index = [
                "OperatingCashFlow",
                "InvestingCashFlow",
                "FinancingCashFlow",
            ]
            cash_flow_q[mock_date]["OperatingCashFlow"] = 28000000000
            cash_flow_q[mock_date]["InvestingCashFlow"] = -8000000000
            cash_flow_q[mock_date]["FinancingCashFlow"] = -20000000000
            ticker_instance.quarterly_cashflow = cash_flow_q

            # Call function
            result = get_quarterly_financial_data("AAPL")

            # Assertions
            self.assertEqual(len(result), 3)
            self.assertIn("income_statement", result)
            self.assertIn("balance_sheet", result)
            self.assertIn("cash_flow", result)

            self.assertEqual(len(result["income_statement"]), 1)
            income_stmt = result["income_statement"][0]
            self.assertEqual(income_stmt.symbol, "AAPL")
            self.assertEqual(income_stmt.statement_type, "income_statement")
            self.assertEqual(income_stmt.period, "quarterly")
            self.assertEqual(income_stmt.date, mock_date)
            self.assertEqual(income_stmt.fiscal_quarter, 1)  # Q1 (Jan-Mar)
            self.assertEqual(income_stmt.fiscal_year, 2022)
            self.assertEqual(income_stmt.data["Revenue"], 97000000000)

            self.assertEqual(len(result["balance_sheet"]), 1)
            balance = result["balance_sheet"][0]
            self.assertEqual(balance.data["TotalAssets"], 350000000000)
            self.assertEqual(balance.fiscal_quarter, 1)

            self.assertEqual(len(result["cash_flow"]), 1)
            cash_flow = result["cash_flow"][0]
            self.assertEqual(cash_flow.data["OperatingCashFlow"], 28000000000)
            self.assertEqual(cash_flow.fiscal_quarter, 1)


if __name__ == "__main__":
    unittest.main()
