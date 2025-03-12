"""
Tests for the collector manager.
"""
import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import pickle
from datetime import datetime, timedelta

from tumkwe_invest.datacollection.collector_manager import CollectorManager
from tumkwe_invest.datacollection.models import DataCollectionTask


class TestCollectorManager(unittest.TestCase):
    """Tests for the collector manager."""
    
    @patch('datacollection.collector_manager.os.makedirs')
    @patch('datacollection.collector_manager.os.path.exists')
    @patch('datacollection.collector_manager.pickle.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_init_and_load_tasks(self, mock_file, mock_pickle_load, mock_exists, mock_makedirs):
        """Test initialization and task loading."""
        # Setup mocks
        mock_exists.return_value = True
        
        # Create sample tasks
        task1 = DataCollectionTask(
            task_name="market_data_AAPL",
            data_type="market_data",
            company_symbols=["AAPL"],
            next_run=datetime.now() + timedelta(hours=1)
        )
        task2 = DataCollectionTask(
            task_name="news_AAPL",
            data_type="news",
            company_symbols=["AAPL"],
            next_run=datetime.now() + timedelta(hours=2)
        )
        mock_pickle_load.return_value = [task1, task2]
        
        # Initialize collector manager
        manager = CollectorManager(output_dir="/tmp/test_data")
        
        # Verify that tasks were loaded
        self.assertEqual(len(manager.tasks), 2)
        self.assertEqual(manager.tasks[0].task_name, "market_data_AAPL")
        self.assertEqual(manager.tasks[1].task_name, "news_AAPL")
        self.assertEqual(len(manager.symbols_monitored), 1)
        self.assertIn("AAPL", manager.symbols_monitored)
    
    @patch('datacollection.collector_manager.os.makedirs')
    @patch('datacollection.collector_manager.os.path.exists')
    @patch('datacollection.collector_manager.pickle.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_tasks(self, mock_file, mock_pickle_dump, mock_exists, mock_makedirs):
        """Test saving tasks."""
        # Setup mocks
        mock_exists.return_value = False
        
        # Initialize collector manager
        manager = CollectorManager(output_dir="/tmp/test_data")
        
        # Create a task and add it
        task = DataCollectionTask(
            task_name="market_data_AAPL",
            data_type="market_data",
            company_symbols=["AAPL"],
            next_run=datetime.now() + timedelta(hours=1)
        )
        manager.tasks.append(task)
        
        # Save tasks
        manager._save_tasks()
        
        # Verify that pickle.dump was called
        mock_pickle_dump.assert_called_once()
        mock_file.assert_called_once()
    
    @patch('datacollection.collector_manager.os.makedirs')
    @patch('datacollection.collector_manager.os.path.exists')
    @patch('datacollection.collector_manager.get_company_profile')
    def test_add_company(self, mock_get_profile, mock_exists, mock_makedirs):
        """Test adding a company."""
        # Setup mocks
        mock_exists.return_value = False
        
        # Create mock profile
        profile = MagicMock()
        profile.name = "Apple Inc."
        mock_get_profile.return_value = profile
        
        # Initialize collector manager with mocked _save_tasks
        manager = CollectorManager(output_dir="/tmp/test_data")
        manager._save_tasks = MagicMock()
        
        # Add a company
        manager.add_company("AAPL")
        
        # Verify that the company was added
        self.assertIn("AAPL", manager.symbols_monitored)
        self.assertEqual(len(manager.tasks), 4)  # 4 tasks should be added
        
        # Verify tasks are of correct types
        task_types = [task.data_type for task in manager.tasks]
        self.assertIn("market_data", task_types)
        self.assertIn("financial_statements", task_types)
        self.assertIn("news", task_types)
        self.assertIn("sec_filings", task_types)
        
        # Verify save was called
        self.assertEqual(manager._save_tasks.call_count, 4)
    
    @patch('datacollection.collector_manager.os.makedirs')
    @patch('datacollection.collector_manager.os.path.exists')
    def test_remove_company(self, mock_exists, mock_makedirs):
        """Test removing a company."""
        # Setup mocks
        mock_exists.return_value = False
        
        # Initialize collector manager with mocked _save_tasks
        manager = CollectorManager(output_dir="/tmp/test_data")
        manager._save_tasks = MagicMock()
        
        # Add company to the monitored set and add some tasks
        manager.symbols_monitored.add("AAPL")
        manager.tasks = [
            DataCollectionTask(
                task_name="market_data_AAPL",
                data_type="market_data",
                company_symbols=["AAPL"],
                next_run=datetime.now() + timedelta(hours=1)
            ),
            DataCollectionTask(
                task_name="news_AAPL",
                data_type="news",
                company_symbols=["AAPL"],
                next_run=datetime.now() + timedelta(hours=2)
            ),
            DataCollectionTask(
                task_name="market_data_MSFT",
                data_type="market_data",
                company_symbols=["MSFT"],
                next_run=datetime.now() + timedelta(hours=1)
            )
        ]
        
        # Remove the company
        manager.remove_company("AAPL")
        
        # Verify the company was removed
        self.assertNotIn("AAPL", manager.symbols_monitored)
        self.assertEqual(len(manager.tasks), 1)  # Only MSFT task remains
        self.assertEqual(manager.tasks[0].company_symbols[0], "MSFT")
        
        # Verify save was called
        manager._save_tasks.assert_called_once()
    
    @patch('datacollection.collector_manager.os.makedirs')
    @patch('datacollection.collector_manager.os.path.exists')
    def test_get_due_tasks(self, mock_exists, mock_makedirs):
        """Test getting due tasks."""
        # Setup mocks
        mock_exists.return_value = False
        
        # Initialize collector manager
        manager = CollectorManager(output_dir="/tmp/test_data")
        
        # Add tasks with different due times
        now = datetime.now()
        past_task = DataCollectionTask(
            task_name="past_task",
            data_type="market_data",
            company_symbols=["AAPL"],
            next_run=now - timedelta(minutes=10)  # Due 10 minutes ago
        )
        future_task = DataCollectionTask(
            task_name="future_task",
            data_type="market_data",
            company_symbols=["MSFT"],
            next_run=now + timedelta(hours=1)  # Due in 1 hour
        )
        manager.tasks = [past_task, future_task]
        
        # Get due tasks
        due_tasks = manager.get_due_tasks()
        
        # Verify only past_task is due
        self.assertEqual(len(due_tasks), 1)
        self.assertEqual(due_tasks[0].task_name, "past_task")
    
    @patch('datacollection.collector_manager.os.makedirs')
    @patch('datacollection.collector_manager.os.path.exists')
    @patch('datacollection.collector_manager.threading.Thread')
    def test_start_stop_collection_thread(self, mock_thread, mock_exists, mock_makedirs):
        """Test starting and stopping the collection thread."""
        # Setup mocks
        mock_exists.return_value = False
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        # Initialize collector manager
        manager = CollectorManager(output_dir="/tmp/test_data")
        
        # Start collection thread
        manager.start_collection_thread()
        
        # Verify thread was started
        self.assertTrue(manager.running)
        self.assertIsNotNone(manager.thread)
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
        
        # Stop collection thread
        manager.stop_collection_thread()
        
        # Verify thread was stopped
        self.assertFalse(manager.running)
        mock_thread_instance.join.assert_called_once()
    
    @patch('datacollection.collector_manager.os.makedirs')
    @patch('datacollection.collector_manager.os.path.exists')
    def test_get_company_dir(self, mock_exists, mock_makedirs):
        """Test getting company directory."""
        # Setup mocks
        mock_exists.return_value = False
        
        # Initialize collector manager
        manager = CollectorManager(output_dir="/tmp/test_data")
        
        # Get company directory
        company_dir = manager._get_company_dir("AAPL")
        
        # Verify directory path
        self.assertEqual(company_dir, "/tmp/test_data/AAPL")
        mock_makedirs.assert_called_once_with("/tmp/test_data/AAPL", exist_ok=True)
    
    @patch('datacollection.collector_manager.os.makedirs')
    @patch('datacollection.collector_manager.os.path.exists')
    @patch('datacollection.collector_manager.generate_combined_report')
    def test_get_validation_summary(self, mock_generate_report, mock_exists, mock_makedirs):
        """Test getting validation summary."""
        # Setup mocks
        mock_exists.return_value = False
        mock_generate_report.return_value = {"status": "ok", "validation_rate": 0.95}
        
        # Initialize collector manager
        manager = CollectorManager(output_dir="/tmp/test_data")
        
        # Add some validation reports
        manager.last_validation = {
            "report1": MagicMock(),
            "report2": MagicMock()
        }
        
        # Get validation summary
        summary = manager.get_validation_summary()
        
        # Verify summary
        self.assertEqual(summary["status"], "ok")
        self.assertEqual(summary["validation_rate"], 0.95)
        mock_generate_report.assert_called_once()


if __name__ == "__main__":
    unittest.main()
