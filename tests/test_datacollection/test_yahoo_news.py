"""
Tests for the Yahoo Finance news collector.
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

from tumkwe_invest.datacollection.collectors.yahoo_news import get_yahoo_finance_news


class TestYahooNews(unittest.TestCase):
    """Tests for the Yahoo Finance news collector."""
    
    @patch('datacollection.collectors.yahoo_news.yf.Ticker')
    def test_get_yahoo_finance_news(self, mock_ticker_class):
        """Test Yahoo Finance news collection."""
        # Create mock ticker
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        
        # Create mock news data
        mock_news = [
            {
                'title': 'Apple Announces New iPhone',
                'publisher': 'Tech News',
                'providerPublishTime': 1673456789,  # Unix timestamp
                'link': 'https://example.com/news/apple-iphone',
                'summary': 'Apple unveiled its new iPhone with improved features.'
            },
            {
                'title': 'Apple Reports Record Earnings',
                'publisher': 'Business Weekly',
                'providerPublishTime': 1673556789,  # Unix timestamp
                'link': 'https://example.com/news/apple-earnings',
                'summary': 'Apple Inc. reported record earnings for the quarter.'
            }
        ]
        
        # Configure the mock
        mock_ticker.news = mock_news
        
        # Call the function
        results = get_yahoo_finance_news("AAPL")
        
        # Validate the results
        self.assertEqual(len(results), 2)
        
        # Check first article
        self.assertEqual(results[0].company_symbol, "AAPL")
        self.assertEqual(results[0].title, "Apple Announces New iPhone")
        self.assertEqual(results[0].publication, "Tech News")
        self.assertEqual(results[0].url, "https://example.com/news/apple-iphone")
        self.assertEqual(results[0].summary, "Apple unveiled its new iPhone with improved features.")
        
        # Check second article
        self.assertEqual(results[1].company_symbol, "AAPL")
        self.assertEqual(results[1].title, "Apple Reports Record Earnings")
        self.assertEqual(results[1].publication, "Business Weekly")
        self.assertEqual(results[1].url, "https://example.com/news/apple-earnings")
        self.assertEqual(results[1].summary, "Apple Inc. reported record earnings for the quarter.")
    
    @patch('datacollection.collectors.yahoo_news.yf.Ticker')
    def test_get_yahoo_finance_news_error_handling(self, mock_ticker_class):
        """Test error handling in Yahoo Finance news collection."""
        # Configure the mock to raise an exception
        mock_ticker_class.side_effect = Exception("Connection error")
        
        # Call the function - it should handle the error and return an empty list
        results = get_yahoo_finance_news("AAPL")
        
        # Validate the results
        self.assertEqual(len(results), 0)
    
    @patch('datacollection.collectors.yahoo_news.yf.Ticker')
    def test_get_yahoo_finance_news_max_articles(self, mock_ticker_class):
        """Test limiting the number of articles."""
        # Create mock ticker
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        
        # Create mock news data with 5 articles
        mock_news = [
            {
                'title': f'Article {i}',
                'publisher': f'Publisher {i}',
                'providerPublishTime': 1673456789 + i,
                'link': f'https://example.com/news/{i}',
                'summary': f'Summary {i}'
            }
            for i in range(5)
        ]
        
        # Configure the mock
        mock_ticker.news = mock_news
        
        # Call the function with max_articles=3
        results = get_yahoo_finance_news("AAPL", max_articles=3)
        
        # Validate that only 3 articles were returned
        self.assertEqual(len(results), 3)


if __name__ == "__main__":
    unittest.main()
