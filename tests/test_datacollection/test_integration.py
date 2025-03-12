"""
Integration tests for the data collection system.
"""
import unittest
import os
import shutil
import tempfile
import json
import pandas as pd
from datetime import datetime, timedelta

from tumkwe_invest.datacollection.collector_manager import CollectorManager
from tumkwe_invest.datacollection.models import StockPrice, CompanyProfile, NewsArticle, SECFiling, KeyMetrics


class TestIntegration(unittest.TestCase):
    """Integration tests for the data collection system."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize the collector manager with the temporary directory
        self.manager = CollectorManager(output_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_minimal_data_flow(self):
        """Test the basic data flow for a minimal collection."""
        # Setup a sample StockPrice object
        price = StockPrice(
            symbol="AAPL",
            source="test",
            date=datetime(2023, 1, 1),
            open=150.0,
            high=155.0,
            low=148.0,
            close=153.0,
            volume=10000000,
            adjusted_close=152.5
        )
        
        # Get company directory
        company_dir = self.manager._get_company_dir("AAPL")
        
        # Save the price data manually (simulating collection)
        prices_file = os.path.join(company_dir, "stock_prices.csv")
        pd.DataFrame([{
            'date': price.date.date().isoformat(),
            'open': price.open,
            'high': price.high,
            'low': price.low,
            'close': price.close,
            'volume': price.volume,
            'adjusted_close': price.adjusted_close,
            'is_valid': True
        }]).to_csv(prices_file, index=False)
        
        # Verify the file was created
        self.assertTrue(os.path.exists(prices_file))
        
        # Read back the data
        df = pd.read_csv(prices_file)
        self.assertEqual(len(df), 1)
        self.assertEqual(df['close'][0], 153.0)
    
    def test_data_validation_flow(self):
        """Test the data validation process."""
        # Setup valid and invalid prices
        valid_price = StockPrice(
            symbol="AAPL",
            source="test",
            date=datetime(2023, 1, 1),
            open=150.0,
            high=155.0,
            low=148.0,
            close=153.0,
            volume=10000000,
            adjusted_close=152.5
        )
        
        invalid_price = StockPrice(
            symbol="AAPL",
            source="test",
            date=datetime(2023, 1, 2),
            open=150.0,
            high=145.0,  # High less than low - invalid
            low=148.0,
            close=153.0,
            volume=10000000,
            adjusted_close=152.5
        )
        
        # Get validation reports
        from tumkwe_invest.datacollection.validation import validate_stock_prices
        report = validate_stock_prices([valid_price, invalid_price], "AAPL")
        
        # Check validation report
        self.assertEqual(report.total_records, 2)
        self.assertEqual(report.valid_records, 1)
        self.assertTrue(len(report.issues) > 0)
        
        # Check that the prices were updated with validation info
        self.assertTrue(valid_price.is_valid)
        self.assertFalse(invalid_price.is_valid)
        self.assertTrue(len(invalid_price.validation_warnings) > 0)
    
    def test_collection_task_management(self):
        """Test adding and managing collection tasks."""
        # Add a company to monitor
        self.manager.add_company("TSLA")
        
        # Check that tasks were created
        self.assertEqual(len(self.manager.tasks), 4)  # 4 task types
        self.assertTrue(all(task.company_symbols[0] == "TSLA" for task in self.manager.tasks))
        
        # Test due task detection
        now = datetime.now()
        
        # Set one task to be due
        self.manager.tasks[0].next_run = now - timedelta(minutes=5)
        # Set another task for the future
        self.manager.tasks[1].next_run = now + timedelta(hours=1)
        
        due_tasks = self.manager.get_due_tasks()
        self.assertEqual(len(due_tasks), 1)
        self.assertEqual(due_tasks[0].company_symbols[0], "TSLA")
        
        # Test removing a company
        self.manager.remove_company("TSLA")
        self.assertEqual(len(self.manager.tasks), 0)
        self.assertFalse("TSLA" in self.manager.symbols_monitored)
    
    def test_file_persistence(self):
        """Test that data is correctly persisted to files."""
        company_dir = self.manager._get_company_dir("TEST")
        
        # Create test data
        profile = CompanyProfile(
            symbol="TEST",
            source="test",
            name="Test Company",
            sector="Technology",
            industry="Software",
            description="A test company"
        )
        
        news = NewsArticle(
            company_symbol="TEST",
            title="Test News",
            publication="Test Source",
            date=datetime(2023, 1, 1),
            url="https://example.com/test",
            summary="Test summary",
            content="Test content"
        )
        
        metrics = KeyMetrics(
            symbol="TEST",
            source="test",
            date=datetime(2023, 1, 1),
            pe_ratio=20.5,
            pb_ratio=2.5,
            dividend_yield=0.02,
            eps=5.0
        )
        
        # Save profile data
        profile_file = os.path.join(company_dir, "profile.json")
        with open(profile_file, 'w') as f:
            profile_dict = {k: v for k, v in profile.__dict__.items() 
                          if not k.startswith('_') and k != 'validation_warnings'}
            profile_dict['last_updated'] = profile_dict['last_updated'].isoformat()
            json.dump(profile_dict, f, indent=4)
        
        # Save news data
        news_file = os.path.join(company_dir, "news_articles.csv")
        news_df = pd.DataFrame([{
            'title': news.title,
            'publication': news.publication,
            'date': news.date.isoformat(),
            'url': news.url,
            'summary': news.summary,
            'sentiment': None,
            'is_valid': True
        }])
        news_df.to_csv(news_file, index=False)
        
        # Save metrics data
        metrics_file = os.path.join(company_dir, "key_metrics.json")
        with open(metrics_file, 'w') as f:
            metrics_dict = {k: v for k, v in metrics.__dict__.items() 
                          if not k.startswith('_') and k != 'validation_warnings'}
            metrics_dict['date'] = metrics_dict['date'].isoformat()
            metrics_dict['last_updated'] = metrics_dict['last_updated'].isoformat()
            json.dump(metrics_dict, f, indent=4)
        
        # Verify all files were created
        self.assertTrue(os.path.exists(profile_file))
        self.assertTrue(os.path.exists(news_file))
        self.assertTrue(os.path.exists(metrics_file))
        
        # Read back the data to verify integrity
        with open(profile_file, 'r') as f:
            loaded_profile = json.load(f)
            self.assertEqual(loaded_profile['name'], "Test Company")
            self.assertEqual(loaded_profile['sector'], "Technology")
        
        loaded_news_df = pd.read_csv(news_file)
        self.assertEqual(len(loaded_news_df), 1)
        self.assertEqual(loaded_news_df.iloc[0]['title'], "Test News")
        
        with open(metrics_file, 'r') as f:
            loaded_metrics = json.load(f)
            self.assertEqual(loaded_metrics['pe_ratio'], 20.5)
            self.assertEqual(loaded_metrics['dividend_yield'], 0.02)


if __name__ == "__main__":
    unittest.main()
