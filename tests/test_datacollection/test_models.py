"""
Tests for the data models.
"""
import unittest
from datetime import datetime, timedelta

from tumkwe_invest.datacollection.models import (
    StockPrice, FinancialStatement, CompanyProfile,
    NewsArticle, KeyMetrics, SECFiling,
    DataCollectionTask, ValidationReport,
    StatementType, Period
)


class TestModels(unittest.TestCase):
    """Tests for the data models."""
    
    def test_stock_price(self):
        """Test StockPrice model."""
        price = StockPrice(
            symbol="AAPL",
            source="yahoo_finance",
            date=datetime(2023, 1, 1),
            open=150.0,
            high=155.0,
            low=148.0,
            close=153.0,
            volume=10000000,
            adjusted_close=152.5
        )
        
        self.assertEqual(price.symbol, "AAPL")
        self.assertEqual(price.open, 150.0)
        self.assertEqual(price.high, 155.0)
        self.assertEqual(price.low, 148.0)
        self.assertEqual(price.close, 153.0)
        self.assertEqual(price.volume, 10000000)
        self.assertEqual(price.adjusted_close, 152.5)
        self.assertTrue(price.is_valid)  # Default is True
        self.assertEqual(price.validation_warnings, [])  # Default is empty list
    
    def test_financial_statement(self):
        """Test FinancialStatement model."""
        statement = FinancialStatement(
            symbol="AAPL",
            source="yahoo_finance",
            statement_type=StatementType.INCOME.value,
            period=Period.ANNUAL.value,
            date=datetime(2023, 1, 1),
            data={
                "Total Revenue": 100000000.0,
                "Net Income": 20000000.0
            }
        )
        
        self.assertEqual(statement.symbol, "AAPL")
        self.assertEqual(statement.statement_type, "income_statement")
        self.assertEqual(statement.period, "annual")
        self.assertEqual(statement.data["Total Revenue"], 100000000.0)
        self.assertEqual(statement.data["Net Income"], 20000000.0)
        self.assertEqual(statement.currency, "USD")  # Default
    
    def test_company_profile(self):
        """Test CompanyProfile model."""
        profile = CompanyProfile(
            symbol="AAPL",
            source="yahoo_finance",
            name="Apple Inc.",
            sector="Technology",
            industry="Consumer Electronics",
            description="Apple Inc. designs, manufactures, and markets smartphones...",
            website="https://www.apple.com"
        )
        
        self.assertEqual(profile.symbol, "AAPL")
        self.assertEqual(profile.name, "Apple Inc.")
        self.assertEqual(profile.sector, "Technology")
        self.assertEqual(profile.industry, "Consumer Electronics")
        self.assertEqual(profile.website, "https://www.apple.com")
    
    def test_news_article(self):
        """Test NewsArticle model."""
        article = NewsArticle(
            company_symbol="AAPL",
            title="Apple Announces New iPhone",
            publication="Tech News",
            date=datetime(2023, 9, 12),
            url="https://example.com/news/apple-iphone",
            summary="Apple unveiled its new iPhone with improved features."
        )
        
        self.assertEqual(article.company_symbol, "AAPL")
        self.assertEqual(article.title, "Apple Announces New iPhone")
        self.assertEqual(article.publication, "Tech News")
        self.assertEqual(article.summary, "Apple unveiled its new iPhone with improved features.")
        self.assertIsNone(article.sentiment)  # Default is None
    
    def test_key_metrics(self):
        """Test KeyMetrics model."""
        metrics = KeyMetrics(
            symbol="AAPL",
            source="yahoo_finance",
            date=datetime(2023, 1, 1),
            pe_ratio=20.5,
            pb_ratio=15.2,
            dividend_yield=0.005,
            eps=6.15
        )
        
        self.assertEqual(metrics.symbol, "AAPL")
        self.assertEqual(metrics.pe_ratio, 20.5)
        self.assertEqual(metrics.pb_ratio, 15.2)
        self.assertEqual(metrics.dividend_yield, 0.005)
        self.assertEqual(metrics.eps, 6.15)
    
    def test_sec_filing(self):
        """Test SECFiling model."""
        filing = SECFiling(
            company_symbol="AAPL",
            filing_type="10-K",
            filing_date=datetime(2022, 10, 28),
            accession_number="0000320193-22-000108"
        )
        
        self.assertEqual(filing.company_symbol, "AAPL")
        self.assertEqual(filing.filing_type, "10-K")
        self.assertEqual(filing.accession_number, "0000320193-22-000108")
        self.assertIsNone(filing.document_text)  # Default is None
    
    def test_data_collection_task(self):
        """Test DataCollectionTask model."""
        now = datetime.now()
        task = DataCollectionTask(
            task_name="market_data_AAPL",
            data_type="market_data",
            company_symbols=["AAPL"],
            next_run=now + timedelta(hours=1)
        )
        
        self.assertEqual(task.task_name, "market_data_AAPL")
        self.assertEqual(task.data_type, "market_data")
        self.assertEqual(task.company_symbols, ["AAPL"])
        self.assertGreater(task.next_run, now)
    
    def test_validation_report(self):
        """Test ValidationReport model."""
        report = ValidationReport(
            data_type="stock_prices",
            company_symbol="AAPL",
            source="yahoo_finance",
            total_records=100,
            valid_records=95
        )
        
        self.assertEqual(report.data_type, "stock_prices")
        self.assertEqual(report.company_symbol, "AAPL")
        self.assertEqual(report.source, "yahoo_finance")
        self.assertEqual(report.total_records, 100)
        self.assertEqual(report.valid_records, 95)
        self.assertEqual(report.issues, {})  # Default is empty dict


if __name__ == "__main__":
    unittest.main()
