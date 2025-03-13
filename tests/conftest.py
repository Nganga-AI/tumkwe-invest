"""
Test configuration and fixtures for Tumkwe Invest.
This file combines test configuration from multiple modules:
- Config testing
- Test runner utilities
- UI testing utilities
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from tumkwe_invest.datacollection.config import (
    CACHE_DIRECTORY,
    DATA_REFRESH_INTERVAL,
    VALIDATION,
)


#
# Config Tests
#
class TestConfig(unittest.TestCase):
    """Tests for the config module."""

    @patch.dict(os.environ, {"ALPHA_VANTAGE_API_KEY": "test_key"})
    def test_environment_variable_loading(self):
        """Test that environment variables are loaded correctly."""
        # Re-import to reload with the mocked environment
        from importlib import reload

        import tumkwe_invest.datacollection.config

        reload(tumkwe_invest.datacollection.config)

        self.assertEqual(
            tumkwe_invest.datacollection.config.ALPHA_VANTAGE_API_KEY, "test_key"
        )

    def test_refresh_intervals(self):
        """Test refresh interval configuration."""
        self.assertIsInstance(DATA_REFRESH_INTERVAL["market_data"], timedelta)
        self.assertIsInstance(DATA_REFRESH_INTERVAL["financial_statements"], timedelta)
        self.assertIsInstance(DATA_REFRESH_INTERVAL["news"], timedelta)
        self.assertIsInstance(DATA_REFRESH_INTERVAL["sec_filings"], timedelta)

    def test_cache_directory_creation(self):
        """Test that the cache directory is created."""
        self.assertTrue(os.path.exists(CACHE_DIRECTORY))

    def test_validation_settings(self):
        """Test validation settings."""
        self.assertIn("max_price_change_percent", VALIDATION)
        self.assertIn("min_data_completeness", VALIDATION)
        self.assertIn("max_pe_ratio", VALIDATION)
        self.assertIn("max_outlier_std", VALIDATION)


#
# Test Runner
#
class IntegrationTestRunner(unittest.TextTestRunner):
    """
    Custom test runner that allows for integration tests to be run only when specified.

    Set the environment variable RUN_INTEGRATION_TESTS=1 to run integration tests.
    """

    def run(self, test):
        """
        Run the test suite, skipping integration tests if not explicitly enabled.
        """
        run_integration = os.environ.get("RUN_INTEGRATION_TESTS") == "1"

        # Mark integration tests to skip if not running integration tests
        if not run_integration:
            for test_case in test:
                if isinstance(test_case, unittest.TestCase):
                    if "Integration" in test_case.__class__.__name__:
                        setattr(
                            test_case,
                            "setUp",
                            lambda: test_case.skipTest("Integration tests disabled"),
                        )
                else:
                    # Handle test suites
                    for sub_test in test_case:
                        if isinstance(sub_test, unittest.TestCase):
                            if "Integration" in sub_test.__class__.__name__:
                                setattr(
                                    sub_test,
                                    "setUp",
                                    lambda: sub_test.skipTest(
                                        "Integration tests disabled"
                                    ),
                                )

        return super().run(test)


def run_all_tests():
    """
    Run all tests in the project.
    """
    # Find test directory
    test_dir = Path(__file__).parent

    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_dir))

    # Run tests with custom runner
    runner = IntegrationTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())


#
# UI Testing Utilities
#
class TestDataGenerator:
    """Utility class to generate test data for UI components."""

    @staticmethod
    def get_sample_dates():
        """Sample dates for testing."""
        today = datetime.now()
        return [
            (today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30, 0, -1)
        ]

    @staticmethod
    def get_sample_price_data():
        """Sample stock price data for testing."""
        sample_dates = TestDataGenerator.get_sample_dates()
        base_price = 180.0
        prices = []
        volumes = []

        for i in range(30):
            change = (i % 5 - 2) * 0.5  # Create some cyclical patterns
            random_factor = (i % 7) * 0.3  # Add some randomness
            price = base_price + change + random_factor
            volume = int(5000000 + (i % 5) * 1000000)

            prices.append(price)
            volumes.append(volume)

        return {"dates": sample_dates, "prices": prices, "volumes": volumes}

    @staticmethod
    def get_technical_indicators():
        """Sample technical indicators for testing."""
        price_data = TestDataGenerator.get_sample_price_data()
        prices = price_data["prices"]
        return {
            "rsi": [45 + (i % 10) for i in range(30)],
            "macd": [0.5 + (i % 5) * 0.1 for i in range(30)],
            "macd_signal": [0.4 + (i % 5) * 0.1 for i in range(30)],
            "moving_averages": {
                "MA50": [p * 0.98 for p in prices],
                "MA200": [p * 0.95 for p in prices],
            },
        }

    @staticmethod
    def get_fundamental_metrics():
        """Sample fundamental metrics for testing."""
        return {
            "pe_ratio": {"value": 28.5, "industry_avg": 25.0},
            "roe": {"value": 0.35, "industry_avg": 0.28},
            "profit_margin": {"value": 0.22, "industry_avg": 0.18},
            "debt_to_equity": {"value": 1.2, "industry_avg": 1.5},
            "current_ratio": {"value": 1.8, "industry_avg": 1.5},
        }

    @staticmethod
    def get_sentiment_data():
        """Sample sentiment data for testing."""
        sample_dates = TestDataGenerator.get_sample_dates()
        return {
            "overall_score": 0.65,
            "summary": "Recent iPhone sales data and positive analyst coverage contribute to bullish sentiment",
            "news_items": [
                {
                    "title": "Apple Reports Strong Q3 Results",
                    "source": "Financial Times",
                    "date": sample_dates[5],
                    "sentiment": 0.8,
                    "url": "https://example.com/news1",
                },
                {
                    "title": "New iPhone Pro Max Sets Sales Record",
                    "source": "Tech Today",
                    "date": sample_dates[3],
                    "sentiment": 0.9,
                    "url": "https://example.com/news2",
                },
                {
                    "title": "Apple Faces Supply Chain Challenges",
                    "source": "Wall Street Journal",
                    "date": sample_dates[7],
                    "sentiment": -0.2,
                    "url": "https://example.com/news3",
                },
            ],
            "integrated_score": 72,
        }

    @staticmethod
    def get_ui_component_config():
        """Sample UI component configuration."""
        return {
            "cards": [
                {
                    "title": "Price",
                    "content": {
                        "value": "$185.92",
                        "description": "Current price",
                        "trend": "+1.2%",
                        "trendDirection": "up",
                    },
                },
                {
                    "title": "Technical Health",
                    "content": {
                        "value": "Strong",
                        "description": "Technical indicators look positive",
                    },
                },
            ],
            "charts": [
                {
                    "type": "line",
                    "data": {
                        "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
                        "datasets": [
                            {"label": "Stock Price", "data": [150, 155, 160, 158, 162]}
                        ],
                    },
                }
            ],
        }


if __name__ == "__main__":
    run_all_tests()
