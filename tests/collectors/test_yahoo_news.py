"""
Tests for Yahoo News data collector.
"""
import datetime
import unittest
from unittest.mock import patch, MagicMock

from tumkwe_invest.datacollection.collectors.yahoo_news import get_yahoo_finance_news


class TestYahooNews(unittest.TestCase):

    def test_get_yahoo_finance_news(self):
        # Setup mock data
        with patch('yfinance.Ticker') as mock:
            ticker_instance = MagicMock()
            mock.return_value = ticker_instance
            
            ticker_instance.news = [
                {
                    "content": {
                        "title": "Apple announces new iPhone",
                        "pubDate": "2023-09-12T15:30:00Z",
                        "provider": {"displayName": "TechNews"},
                        "clickThroughUrl": {"url": "https://example.com/news1"},
                        "summary": "Apple has announced its latest iPhone model with new features.",
                    }
                },
                {
                    "content": {
                        "title": "Apple Q3 Earnings Beat Expectations",
                        "pubDate": "2023-08-01T18:45:00Z",
                        "provider": {"displayName": "Financial Times"},
                        "clickThroughUrl": {"url": "https://example.com/news2"},
                        "summary": "Apple reported strong Q3 earnings above analyst expectations.",
                    }
                }
            ]

            # Call function
            result = get_yahoo_finance_news("AAPL", max_articles=2)

            # Assertions
            self.assertEqual(len(result), 2)
            
            article1 = result[0]
            self.assertEqual(article1.company_symbol, "AAPL")
            self.assertEqual(article1.title, "Apple announces new iPhone")
            self.assertEqual(article1.publication, "TechNews")
            self.assertEqual(article1.date, datetime.datetime(2023, 9, 12, 15, 30, 0))
            self.assertEqual(article1.url, "https://example.com/news1")
            self.assertEqual(article1.summary, "Apple has announced its latest iPhone model with new features.")

            article2 = result[1]
            self.assertEqual(article2.company_symbol, "AAPL")
            self.assertEqual(article2.title, "Apple Q3 Earnings Beat Expectations")
            self.assertEqual(article2.publication, "Financial Times")
            self.assertEqual(article2.date, datetime.datetime(2023, 8, 1, 18, 45, 0))
            self.assertEqual(article2.url, "https://example.com/news2")
            self.assertEqual(article2.summary, "Apple reported strong Q3 earnings above analyst expectations.")

    def test_get_yahoo_finance_news_max_limit(self):
        # Setup mock data with more articles than max_articles
        with patch('yfinance.Ticker') as mock:
            ticker_instance = MagicMock()
            mock.return_value = ticker_instance
            
            ticker_instance.news = [{"content": {"title": f"News Article {i}", "pubDate": "2023-09-12T15:30:00Z"}} for i in range(10)]

            # Call function with max_articles=3
            result = get_yahoo_finance_news("AAPL", max_articles=3)

            # Should only return 3 articles
            self.assertEqual(len(result), 3)

    def test_get_yahoo_finance_news_error(self):
        # Setup mock to raise exception
        with patch('yfinance.Ticker') as mock:
            ticker_instance = MagicMock()
            mock.return_value = ticker_instance
            
            ticker_instance.news.__getitem__.side_effect = Exception("API Error")

            # Call function
            result = get_yahoo_finance_news("AAPL")

            # Should return empty list on error
            self.assertEqual(result, [])

    def test_get_yahoo_finance_news_missing_data(self):
        # Setup mock with missing data
        with patch('yfinance.Ticker') as mock:
            ticker_instance = MagicMock()
            mock.return_value = ticker_instance
            
            ticker_instance.news = [
                {
                    "content": {
                        # Missing title
                        "pubDate": "2023-09-12T15:30:00Z",
                        # Missing provider
                        "clickThroughUrl": {"url": "https://example.com/news1"},
                        # Missing summary
                    }
                }
            ]

            # Call function
            result = get_yahoo_finance_news("AAPL")

            # Should handle missing data gracefully
            self.assertEqual(len(result), 1)
            article = result[0]
            self.assertEqual(article.title, "")
            self.assertEqual(article.publication, "Yahoo Finance")  # Default value
            self.assertEqual(article.summary, "")


if __name__ == "__main__":
    unittest.main()
