"""
Performance tests for the data collection system.
"""
import unittest
import time
import os
import tempfile
import shutil
from datetime import datetime, timedelta

from datacollection.collector_manager import CollectorManager
from datacollection.collectors.yahoo_finance import get_stock_data
from datacollection.collectors.yahoo_news import get_yahoo_finance_news


class TestPerformance(unittest.TestCase):
    """Performance tests for the data collection system."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        
        # Set test parameters
        self.symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
        self.start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        self.end_date = datetime.now().strftime("%Y-%m-%d")
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_stock_data_collection_performance(self):
        """Test the performance of stock data collection."""
        total_time = 0
        total_records = 0
        
        for symbol in self.symbols:
            start_time = time.time()
            
            # Get the stock data
            prices = get_stock_data(symbol, self.start_date, self.end_date)
            
            end_time = time.time()
            elapsed = end_time - start_time
            total_time += elapsed
            
            # Count records
            if prices:
                total_records += len(prices)
            
            print(f"{symbol}: {len(prices) if prices else 0} records in {elapsed:.2f} seconds")
        
        avg_time_per_symbol = total_time / len(self.symbols)
        avg_time_per_record = total_time / total_records if total_records > 0 else 0
        
        print(f"\nPerformance summary:")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Average time per symbol: {avg_time_per_symbol:.2f} seconds")
        print(f"Average time per record: {avg_time_per_record:.4f} seconds")
        print(f"Records per second: {total_records / total_time:.2f}")
        
        # Basic performance assertion - should be able to process at least 10 records per second
        self.assertGreater(total_records / total_time, 10)
    
    def test_news_collection_performance(self):
        """Test the performance of news collection."""
        total_time = 0
        total_articles = 0
        
        for symbol in self.symbols:
            start_time = time.time()
            
            # Get news articles
            articles = get_yahoo_finance_news(symbol, max_articles=10)
            
            end_time = time.time()
            elapsed = end_time - start_time
            total_time += elapsed
            
            # Count articles
            if articles:
                total_articles += len(articles)
            
            print(f"{symbol}: {len(articles) if articles else 0} articles in {elapsed:.2f} seconds")
        
        avg_time_per_symbol = total_time / len(self.symbols)
        avg_time_per_article = total_time / total_articles if total_articles > 0 else 0
        
        print(f"\nPerformance summary:")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Average time per symbol: {avg_time_per_symbol:.2f} seconds")
        print(f"Average time per article: {avg_time_per_article:.4f} seconds")
        print(f"Articles per second: {total_articles / total_time:.2f}")
        
        # Performance assertion - news collection can be slower but should be reasonable
        self.assertLess(avg_time_per_symbol, 10)  # Less than 10 seconds per symbol
    
    def test_collector_manager_scalability(self):
        """Test that the collector manager can handle many companies."""
        manager = CollectorManager(output_dir=self.temp_dir)
        
        # Time how long it takes to add many companies
        start_time = time.time()
        
        # Add a representative sample of companies (20 should be enough for testing)
        test_symbols = self.symbols + ['TSLA', 'NFLX', 'NVDA', 'PYPL', 'INTC', 
                                      'AMD', 'CSCO', 'ADBE', 'CRM', 'IBM',
                                      'ORCL', 'QCOM', 'TXN', 'AVGO', 'MU']
                                      
        for symbol in test_symbols:
            manager.add_company(symbol)
        
        end_time = time.time()
        add_time = end_time - start_time
        
        print(f"Added {len(test_symbols)} companies in {add_time:.2f} seconds")
        print(f"Average time per company: {add_time / len(test_symbols):.4f} seconds")
        
        # Test getting due tasks
        start_time = time.time()
        due_tasks = manager.get_due_tasks()
        end_time = time.time()
        
        print(f"Found {len(due_tasks)} due tasks in {end_time - start_time:.6f} seconds")
        
        # Performance assertion - adding a company should be fast
        self.assertLess(add_time / len(test_symbols), 0.5)  # Less than 0.5 seconds per company
        
        # Performance assertion - getting due tasks should be very fast regardless of company count
        self.assertLess(end_time - start_time, 0.1)  # Less than 0.1 seconds


if __name__ == "__main__":
    unittest.main()
