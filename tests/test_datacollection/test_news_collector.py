"""
Tests for the News API collector.
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

from datacollection.collectors.news_collector import get_company_news


class TestNewsCollector(unittest.TestCase):
    """Tests for the News API collector."""
    
    @patch('datacollection.collectors.news_collector.requests.get')
    @patch('datacollection.collectors.news_collector.NEWS_API_KEY', 'dummy_key')
    def test_get_company_news(self, mock_get):
        """Test news collection with News API."""
        # Create mock response
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            'articles': [
                {
                    'title': 'Apple Announces New iPhone',
                    'source': {'name': 'Tech News'},
                    'publishedAt': '2023-01-12T12:34:56Z',
                    'url': 'https://example.com/news/apple-iphone',
                    'description': 'Apple unveiled its new iPhone with improved features.'
                },
                {
                    'title': 'Apple Reports Record Earnings',
                    'source': {'name': 'Business Weekly'},
                    'publishedAt': '2023-01-15T09:45:00Z',
                    'url': 'https://example.com/news/apple-earnings',
                    'description': 'Apple Inc. reported record earnings for the quarter.'
                }
            ]
        }
        
        # Configure the mock
        mock_get.return_value = mock_response
        
        # Call the function
        results = get_company_news("AAPL", "Apple Inc.")
        
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
    
    @patch('datacollection.collectors.news_collector.NEWS_API_KEY', '')
    def test_get_company_news_no_api_key(self):
        """Test news collection without an API key."""
        # Should return empty list when API key is not set
        results = get_company_news("AAPL", "Apple Inc.")
        self.assertEqual(len(results), 0)
    
    @patch('datacollection.collectors.news_collector.requests.get')
    @patch('datacollection.collectors.news_collector.NEWS_API_KEY', 'dummy_key')
    @patch('datacollection.collectors.news_collector.Article')
    def test_get_company_news_with_content(self, mock_article_class, mock_get):
        """Test news collection with article content download."""
        # Create mock response
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            'articles': [
                {
                    'title': 'Apple Announces New iPhone',
                    'source': {'name': 'Tech News'},
                    'publishedAt': '2023-01-12T12:34:56Z',
                    'url': 'https://example.com/news/apple-iphone',
                    'description': 'Apple unveiled its new iPhone with improved features.'
                }
            ]
        }
        
        # Configure the request mock
        mock_get.return_value = mock_response
        
        # Configure the Article mock
        mock_article = MagicMock()
        mock_article.text = "Full article content about the new iPhone."
        mock_article_class.return_value = mock_article
        
        # Call the function
        results = get_company_news("AAPL", "Apple Inc.")
        
        # Validate the results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content, "Full article content about the new iPhone.")


if __name__ == "__main__":
    unittest.main()
