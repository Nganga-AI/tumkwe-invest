"""
Tests for the unified data collection script.
"""

import unittest
from unittest.mock import MagicMock, patch

from unified_data_collection import collect_data, main, setup_logging


class TestUnifiedCollection(unittest.TestCase):
    """Tests for the unified data collection script."""

    @patch("unified_data_collection.CollectorManager")
    @patch("unified_data_collection.setup_logging")
    def test_collect_data_normal(self, mock_setup_logging, mock_manager_class):
        """Test normal data collection."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        # Call collect_data
        collect_data(["AAPL", "MSFT"])

        # Verify manager was initialized and companies were added
        mock_manager_class.assert_called_once()
        self.assertEqual(mock_manager.add_company.call_count, 2)
        mock_manager.collect_all_data_for_symbol.assert_any_call("AAPL")
        mock_manager.collect_all_data_for_symbol.assert_any_call("MSFT")
        mock_manager.get_validation_summary.assert_called_once()

    @patch("unified_data_collection.CollectorManager")
    @patch("unified_data_collection.setup_logging")
    def test_collect_data_validate_only(self, mock_setup_logging, mock_manager_class):
        """Test validation-only mode."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        # Call collect_data with validate_only=True
        collect_data(["AAPL"], validate_only=True)

        # Verify manager was initialized and companies were added but no collection occurred
        mock_manager_class.assert_called_once()
        mock_manager.add_company.assert_called_once_with("AAPL")
        mock_manager.collect_all_data_for_symbol.assert_not_called()
        mock_manager.get_validation_summary.assert_called_once()

    @patch("unified_data_collection.CollectorManager")
    @patch("unified_data_collection.setup_logging")
    def test_collect_data_scheduler(self, mock_setup_logging, mock_manager_class):
        """Test scheduler mode."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        # Simulate KeyboardInterrupt after starting scheduler
        mock_manager.start_collection_thread.side_effect = KeyboardInterrupt()

        # Call collect_data with scheduler=True
        collect_data(["AAPL"], scheduler=True)

        # Verify manager was initialized and scheduler was started
        mock_manager_class.assert_called_once()
        mock_manager.add_company.assert_called_once_with("AAPL")
        mock_manager.start_collection_thread.assert_called_once()
        mock_manager.stop_collection_thread.assert_called_once()

    @patch("unified_data_collection.collect_data")
    @patch("unified_data_collection.argparse.ArgumentParser.parse_args")
    def test_main_with_symbols(self, mock_parse_args, mock_collect_data):
        """Test main function with command-line symbols."""
        # Setup mock for parsed args
        mock_args = MagicMock()
        mock_args.symbols = ["AAPL", "MSFT"]
        mock_args.file = None
        mock_args.scheduler = False
        mock_args.validate = False
        mock_parse_args.return_value = mock_args

        # Call main
        main()

        # Verify collect_data was called with correct parameters
        mock_collect_data.assert_called_once_with(
            ["AAPL", "MSFT"], scheduler=False, validate_only=False
        )

    @patch("unified_data_collection.collect_data")
    @patch("unified_data_collection.argparse.ArgumentParser.parse_args")
    @patch("unified_data_collection.os.path.exists")
    @patch(
        "builtins.open", new_callable=unittest.mock.mock_open, read_data="AMZN\nTSLA\n"
    )
    def test_main_with_file(
        self, mock_file, mock_exists, mock_parse_args, mock_collect_data
    ):
        """Test main function with symbols from file."""
        # Setup mock for parsed args
        mock_args = MagicMock()
        mock_args.symbols = []
        mock_args.file = "symbols.txt"
        mock_args.scheduler = False
        mock_args.validate = False
        mock_parse_args.return_value = mock_args

        # Setup mock for file existence
        mock_exists.return_value = True

        # Call main
        main()

        # Verify collect_data was called with correct parameters
        mock_collect_data.assert_called_once_with(
            ["AMZN", "TSLA"], scheduler=False, validate_only=False
        )

    def test_setup_logging(self):
        """Test logging setup."""
        # Call setup_logging
        logger = setup_logging()

        # Verify logger was created
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "unified_collector")


if __name__ == "__main__":
    unittest.main()
