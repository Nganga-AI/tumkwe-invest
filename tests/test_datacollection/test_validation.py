"""
Tests for the data validation module.
"""
import unittest
from datetime import datetime, timedelta
import pandas as pd

from tumkwe_invest.datacollection.models import (
    StockPrice, FinancialStatement, CompanyProfile,
    NewsArticle, KeyMetrics, ValidationReport
)
from tumkwe_invest.datacollection.validation import (
    validate_stock_prices, validate_financial_statement,
    validate_key_metrics, validate_company_profile,
    validate_news_articles, generate_combined_report
)


class TestValidation(unittest.TestCase):
    """Tests for the data validation module."""
    
    def test_validate_stock_prices(self):
        """Test stock price validation."""
        # Create sample stock prices
        base_date = datetime(2022, 1, 3)  # Monday
        prices = [
            StockPrice(
                symbol="AAPL",
                source="yahoo_finance",
                date=base_date + timedelta(days=i),
                open=150.0 + i,
                high=155.0 + i,
                low=148.0 + i,
                close=153.0 + i,
                volume=10000000,
                adjusted_close=152.5 + i
            )
            for i in range(5)  # 5 consecutive days
        ]
        
        # Add an invalid price (high < low)
        invalid_price = StockPrice(
            symbol="AAPL",
            source="yahoo_finance",
            date=base_date + timedelta(days=5),
            open=150.0,
            high=145.0,  # High less than low - invalid
            low=148.0,
            close=153.0,
            volume=10000000,
            adjusted_close=152.5
        )
        prices.append(invalid_price)
        
        # Validate the prices
        report = validate_stock_prices(prices, "AAPL")
        
        # Check the report
        self.assertEqual(report.data_type, "stock_prices")
        self.assertEqual(report.company_symbol, "AAPL")
        self.assertEqual(report.total_records, 6)
        self.assertEqual(report.valid_records, 5)  # One invalid record
        self.assertEqual(len(report.issues), 1)  # One issue reported
        
        # Check that the invalid price was marked as such
        self.assertFalse(invalid_price.is_valid)
        self.assertTrue(len(invalid_price.validation_warnings) > 0)
    
    def test_validate_financial_statement(self):
        """Test financial statement validation."""
        # Create a valid income statement
        valid_statement = FinancialStatement(
            symbol="AAPL",
            source="yahoo_finance",
            statement_type="income_statement",
            period="annual",
            date=datetime(2022, 12, 31),
            data={
                "Total Revenue": 100000000.0,
                "Net Income": 20000000.0,
                "Operating Income": 30000000.0,
                "Gross Profit": 40000000.0,
                "EBITDA": 35000000.0
            }
        )
        
        # Validate the statement
        report = validate_financial_statement(valid_statement)
        
        # Check the report
        self.assertEqual(report.valid_records, 1)
        self.assertEqual(len(report.issues), 0)
        self.assertTrue(valid_statement.is_valid)
        
        # Create an invalid statement (missing key fields)
        invalid_statement = FinancialStatement(
            symbol="AAPL",
            source="yahoo_finance",
            statement_type="income_statement",
            period="annual",
            date=datetime(2022, 12, 31),
            data={
                "Total Revenue": 100000000.0,
                # Missing Net Income, Operating Income, etc.
            }
        )
        
        # Validate the invalid statement
        report = validate_financial_statement(invalid_statement)
        
        # Check the report
        self.assertEqual(report.valid_records, 0)
        self.assertTrue(len(report.issues) > 0)
        self.assertFalse(invalid_statement.is_valid)
        
        # Create an invalid balance sheet (doesn't balance)
        unbalanced_statement = FinancialStatement(
            symbol="AAPL",
            source="yahoo_finance",
            statement_type="balance_sheet",
            period="annual",
            date=datetime(2022, 12, 31),
            data={
                "Total Assets": 100000000.0,
                "Total Liabilities": 30000000.0,
                "Total Equity": 60000000.0,  # Assets should equal Liabilities + Equity
                "Cash And Cash Equivalents": 20000000.0,
                "Total Debt": 25000000.0
            }
        )
        
        # Validate the unbalanced statement
        report = validate_financial_statement(unbalanced_statement)
        
        # Check the report
        self.assertEqual(report.valid_records, 0)
        self.assertTrue(len(report.issues) > 0)
        self.assertFalse(unbalanced_statement.is_valid)
    
    def test_validate_key_metrics(self):
        """Test key metrics validation."""
        # Create valid metrics
        valid_metrics = KeyMetrics(
            symbol="AAPL",
            source="yahoo_finance",
            date=datetime(2023, 1, 1),
            pe_ratio=20.5,
            pb_ratio=15.2,
            dividend_yield=0.005,
            eps=6.15
        )
        
        # Validate the metrics
        report = validate_key_metrics(valid_metrics)
        
        # Check the report
        self.assertEqual(report.valid_records, 1)
        self.assertEqual(len(report.issues), 0)
        self.assertTrue(valid_metrics.is_valid)
        
        # Create invalid metrics (negative P/E ratio)
        invalid_metrics = KeyMetrics(
            symbol="AAPL",
            source="yahoo_finance",
            date=datetime(2023, 1, 1),
            pe_ratio=-5.3,
            pb_ratio=15.2,
            dividend_yield=0.005,
            eps=6.15
        )
        
        # Validate the invalid metrics
        report = validate_key_metrics(invalid_metrics)
        
        # Check the report
        self.assertEqual(report.valid_records, 0)
        self.assertTrue(len(report.issues) > 0)
        self.assertFalse(invalid_metrics.is_valid)
        
        # Create invalid metrics (extremely high dividend yield)
        high_yield_metrics = KeyMetrics(
            symbol="AAPL",
            source="yahoo_finance",
            date=datetime(2023, 1, 1),
            pe_ratio=20.5,
            pb_ratio=15.2,
            dividend_yield=0.30,  # 30% yield is suspiciously high
            eps=6.15
        )
        
        # Validate the high yield metrics
        report = validate_key_metrics(high_yield_metrics)
        
        # Check the report
        self.assertEqual(report.valid_records, 0)
        self.assertTrue(len(report.issues) > 0)
        self.assertFalse(high_yield_metrics.is_valid)
    
    def test_validate_company_profile(self):
        """Test company profile validation."""
        # Create valid profile
        valid_profile = CompanyProfile(
            symbol="AAPL",
            source="yahoo_finance",
            name="Apple Inc.",
            sector="Technology",
            industry="Consumer Electronics",
            description="Apple Inc. designs, manufactures, and markets smartphones..."
        )
        
        # Validate the profile
        report = validate_company_profile(valid_profile)
        
        # Check the report
        self.assertEqual(report.valid_records, 1)
        self.assertEqual(len(report.issues), 0)
        self.assertTrue(valid_profile.is_valid)
        
        # Create invalid profile (missing sector)
        invalid_profile = CompanyProfile(
            symbol="AAPL",
            source="yahoo_finance",
            name="Apple Inc.",
            sector="",  # Missing sector
            industry="Consumer Electronics",
            description="Apple Inc. designs, manufactures, and markets smartphones..."
        )
        
        # Validate the invalid profile
        report = validate_company_profile(invalid_profile)
        
        # Check the report
        self.assertEqual(report.valid_records, 0)
        self.assertTrue(len(report.issues) > 0)
        self.assertFalse(invalid_profile.is_valid)
    
    def test_validate_news_articles(self):
        """Test news article validation."""
        # Create valid articles
        articles = [
            NewsArticle(
                company_symbol="AAPL",
                title="Apple Announces New iPhone",
                publication="Tech News",
                date=datetime(2023, 9, 12),
                url="https://example.com/news/apple-iphone",
                summary="Apple unveiled its new iPhone with improved features.",
                content="Full article content about the new iPhone launch event."
            ),
            NewsArticle(
                company_symbol="AAPL",
                title="Apple Reports Record Earnings",
                publication="Business Weekly",
                date=datetime(2023, 7, 15),
                url="https://example.com/news/apple-earnings",
                summary="Apple Inc. reported record earnings for the quarter.",
                content="Detailed analysis of Apple's quarterly financial results."
            )
        ]
        
        # Validate the articles
        report = validate_news_articles(articles, "AAPL")
        
        # Check the report
        self.assertEqual(report.valid_records, 2)
        self.assertEqual(len(report.issues), 0)
        
        # Create an invalid article (missing content)
        invalid_article = NewsArticle(
            company_symbol="AAPL",
            title="Apple Stock Rises",
            publication="Market News",
            date=datetime(2023, 8, 20),
            url="https://example.com/news/apple-stock",
            summary="Apple stock rose 2% today.",
            content=None  # Missing content
        )
        articles.append(invalid_article)
        
        # Validate with the invalid article
        report = validate_news_articles(articles, "AAPL")
        
        # Check the report
        self.assertEqual(report.total_records, 3)
        self.assertEqual(report.valid_records, 2)  # One invalid record
        self.assertTrue(len(report.issues) > 0)
    
    def test_generate_combined_report(self):
        """Test generating a combined validation report."""
        # Create sample validation reports
        price_report = ValidationReport(
            data_type="stock_prices",
            company_symbol="AAPL",
            source="yahoo_finance",
            total_records=100,
            valid_records=95,
            issues={"price_errors": ["5 records with pricing inconsistencies"]}
        )
        
        profile_report = ValidationReport(
            data_type="company_profile",
            company_symbol="AAPL",
            source="yahoo_finance",
            total_records=1,
            valid_records=1
        )
        
        news_report = ValidationReport(
            data_type="news_articles",
            company_symbol="AAPL",
            source="news_api",
            total_records=20,
            valid_records=18,
            issues={"news_errors": ["2 articles missing content"]}
        )
        
        # Generate combined report
        combined = generate_combined_report([price_report, profile_report, news_report])
        
        # Check the combined report
        self.assertEqual(combined["total_records"], 121)
        self.assertEqual(combined["valid_records"], 114)
        self.assertAlmostEqual(combined["validation_rate"], 114/121)
        self.assertEqual(len(combined["data_types"]), 3)
        self.assertEqual(len(combined["issues_by_type"]), 2)


if __name__ == "__main__":
    unittest.main()
