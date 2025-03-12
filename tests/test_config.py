"""
Tests for the config module.
"""

import os
import unittest
from datetime import timedelta
from unittest.mock import patch

from datacollection.config import (
    CACHE_DIRECTORY,
    DATA_REFRESH_INTERVAL,
    VALIDATION,
)


class TestConfig(unittest.TestCase):
    """Tests for the config module."""

    @patch.dict(os.environ, {"ALPHA_VANTAGE_API_KEY": "test_key"})
    def test_environment_variable_loading(self):
        """Test that environment variables are loaded correctly."""
        # Re-import to reload with the mocked environment
        from importlib import reload

        import datacollection.config

        reload(datacollection.config)

        self.assertEqual(datacollection.config.ALPHA_VANTAGE_API_KEY, "test_key")

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


if __name__ == "__main__":
    unittest.main()
