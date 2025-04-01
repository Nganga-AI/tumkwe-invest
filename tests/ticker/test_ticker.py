import unittest
from unittest.mock import patch

# ...existing imports...
from tumkwe_invest.ticker import (
    get_stock_balance_sheet,
    get_stock_cash_flow,
    get_stock_income_statement,
    get_stock_info,
    get_stock_price_history,
    get_stock_recommendations,
)


class FakeTicker:
    def __init__(self, ticker):
        self.ticker = ticker

    def get_info(self):
        return {"info": "dummy"}

    def history(self, period, interval, start, end):
        class Dummy:
            def to_dict(self):
                return {"history": "dummy"}

        return Dummy()

    def get_balance_sheet(self, as_dict, pretty, freq):
        return {"balance": "dummy"}

    def get_income_stmt(self, as_dict, pretty, freq):
        return {"income": "dummy"}

    def get_cash_flow(self, as_dict, pretty, freq):
        return {"cash_flow": "dummy"}

    def get_recommendations(self, as_dict):
        return {"recommendations": "dummy"}


class TestTickerTools(unittest.TestCase):
    @patch("yfinance.Ticker", side_effect=lambda ticker: FakeTicker(ticker))
    def test_get_stock_info(self, mock_ticker):
        result = get_stock_info.invoke({"ticker": "AAPL"})
        self.assertEqual(result, {"info": "dummy"})

    @patch("yfinance.Ticker", side_effect=lambda ticker: FakeTicker(ticker))
    def test_get_stock_price_history(self, mock_ticker):
        result = get_stock_price_history.invoke(
            {
                "ticker": "AAPL",
                "period": "1mo",
                "interval": "1d",
            }
        )
        self.assertEqual(result, {"history": "dummy"})

    @patch("yfinance.Ticker", side_effect=lambda ticker: FakeTicker(ticker))
    def test_get_stock_balance_sheet(self, mock_ticker):
        result = get_stock_balance_sheet.invoke({"ticker": "AAPL", "freq": "yearly"})
        self.assertEqual(result, {"balance": "dummy"})

    @patch("yfinance.Ticker", side_effect=lambda ticker: FakeTicker(ticker))
    def test_get_stock_income_statement(self, mock_ticker):
        result = get_stock_income_statement.invoke({"ticker": "AAPL", "freq": "yearly"})
        self.assertEqual(result, {"income": "dummy"})

    @patch("yfinance.Ticker", side_effect=lambda ticker: FakeTicker(ticker))
    def test_get_stock_cash_flow(self, mock_ticker):
        result = get_stock_cash_flow.invoke({"ticker": "AAPL", "freq": "yearly"})
        self.assertEqual(result, {"cash_flow": "dummy"})

    @patch("yfinance.Ticker", side_effect=lambda ticker: FakeTicker(ticker))
    def test_get_stock_recommendations(self, mock_ticker):
        result = get_stock_recommendations.invoke({"ticker": "AAPL"})
        self.assertEqual(result, {"recommendations": "dummy"})


if __name__ == "__main__":
    unittest.main()
