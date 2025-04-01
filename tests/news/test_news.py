import unittest
from unittest.mock import patch
from datetime import datetime

# ...existing imports...
from tumkwe_invest.news import fetch_company_news

class FakeTickerWithNews:
    def __init__(self, ticker):
        self.ticker = ticker
    def get_news(self, count):
        # Return dummy news with expected inner structure
        return [{
            "content": {
                "title": "Test Title",
                "summary": "Test Summary",
                "pubDate": "2023-10-10",
                "provider": "TestProvider",
            }
        }]

class FakeTickerNoNews:
    def __init__(self, ticker):
        self.ticker = ticker
    def get_news(self, count):
        return None

class FakeSearch:
    def __init__(self, query, enable_fuzzy_query, news_count):
        self.news = [{
            "title": "Fallback Title",
            "publisher": "FallbackPublisher",
            "providerPublishTime": 1700000000,
        }]

class TestNewsTools(unittest.TestCase):
    @patch("yfinance.Ticker", side_effect=lambda ticker: FakeTickerWithNews(ticker))
    def test_fetch_company_news_with_news(self, mock_ticker):
        result = fetch_company_news.invoke({"ticker": "AAPL", "max_articles": 1})
        expected = [{
            "title": "Test Title",
            "summary": "Test Summary",
            "pubDate": "2023-10-10",
            "source": "TestProvider",
        }]
        self.assertEqual(result, expected)
    
    @patch("yfinance.Search", side_effect=lambda query, enable_fuzzy_query, news_count: FakeSearch(query, enable_fuzzy_query, news_count))
    @patch("yfinance.Ticker", side_effect=lambda ticker: FakeTickerNoNews(ticker))
    def test_fetch_company_news_fallback(self, mock_ticker, mock_search):
        result = fetch_company_news.invoke({"ticker": "AAPL", "max_articles": 1})
        # Calculate expected formatted publish time from the timestamp
        expected_pub_time = datetime.fromtimestamp(1700000000).strftime("%Y-%m-%d %H:%M:%S")
        expected = [{
            "title": "Fallback Title",
            "source": "FallbackPublisher",
            "providerPublishTime": expected_pub_time,
        }]
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
