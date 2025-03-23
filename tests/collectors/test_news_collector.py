"""
Tests for the News API collector.
"""

import datetime
import os
import unittest
from unittest.mock import MagicMock, patch

from tumkwe_invest.datacollection.collectors.news_collector import (
    get_company_news,
)


class TestNewsCollector(unittest.TestCase):

    def setUp(self):
        # Save original env vars
        self.original_news_api_key = os.environ.get("NEWS_API_KEY", None)

    def tearDown(self):
        # Restore original env vars
        if self.original_news_api_key is not None:
            os.environ["NEWS_API_KEY"] = self.original_news_api_key
        elif "NEWS_API_KEY" in os.environ:
            del os.environ["NEWS_API_KEY"]

    def test_get_company_news(self):
        # Setup environment and mocks
        os.environ["NEWS_API_KEY"] = "fake-api-key"

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_get.return_value = mock_response

            # Mock the API response
            mock_response.json.return_value = {
                "status": "ok",
                "totalResults": 2,
                "articles": [
                    {
                        "source": {"id": "techcrunch", "name": "TechCrunch"},
                        "title": "Microsoft announces new Windows features",
                        "description": "Microsoft is rolling out new features for Windows users.",
                        "url": "https://example.com/news1",
                        "publishedAt": "2023-09-10T14:30:00Z",
                    },
                    {
                        "source": {"id": "cnbc", "name": "CNBC"},
                        "title": "Microsoft stock hits all-time high",
                        "description": "Microsoft's stock reached a new record today.",
                        "url": "https://example.com/news2",
                        "publishedAt": "2023-09-09T10:15:00Z",
                    },
                ],
            }

            # Call function
            result = get_company_news(
                company_symbol="MSFT", company_name="Microsoft", days=5, max_articles=10
            )

            # Assertions
            self.assertEqual(len(result), 2)

            article1 = result[0]
            self.assertEqual(article1.company_symbol, "MSFT")
            self.assertEqual(article1.title, "Microsoft announces new Windows features")
            self.assertEqual(article1.publication, "TechCrunch")
            self.assertEqual(article1.date, datetime.datetime(2023, 9, 10, 14, 30))
            self.assertEqual(article1.url, "https://example.com/news1")
            self.assertEqual(
                article1.summary,
                "Microsoft is rolling out new features for Windows users.",
            )

            article2 = result[1]
            self.assertEqual(article2.company_symbol, "MSFT")
            self.assertEqual(article2.title, "Microsoft stock hits all-time high")
            self.assertEqual(article2.publication, "CNBC")
            self.assertEqual(article2.date, datetime.datetime(2023, 9, 9, 10, 15))
            self.assertEqual(article2.url, "https://example.com/news2")
            self.assertEqual(
                article2.summary, "Microsoft's stock reached a new record today."
            )

            # Check that the API was called with the right parameters
            mock_get.assert_called_once()
            args, kwargs = mock_get.call_args
            self.assertEqual(kwargs["params"]["q"], "Microsoft")
            self.assertEqual(kwargs["params"]["language"], "en")
            self.assertEqual(kwargs["params"]["sortBy"], "popularity")
            self.assertEqual(kwargs["params"]["pageSize"], 10)
            self.assertEqual(kwargs["params"]["apiKey"], "fake-api-key")

    def test_get_company_news_no_api_key(self):
        # Ensure the API key is not set
        if "NEWS_API_KEY" in os.environ:
            del os.environ["NEWS_API_KEY"]

        # Call function
        result = get_company_news(company_symbol="MSFT", company_name="Microsoft")

        # Should return empty list when API key is not available
        self.assertEqual(result, [])

    def test_get_company_news_no_company_provided(self):
        # Should raise ValueError when neither symbol nor name is provided
        with self.assertRaises(ValueError):
            get_company_news()

    def test_get_company_news_api_error(self):
        # Setup environment and mocks
        os.environ["NEWS_API_KEY"] = "fake-api-key"

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_get.return_value = mock_response

            # Mock an API error
            mock_response.raise_for_status.side_effect = Exception("API Error")

            # Call function
            result = get_company_news(company_symbol="MSFT", company_name="Microsoft")

            # Should return empty list on API error
            self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
