"""Test cases for the dashboard module."""

import unittest
from datetime import datetime, timedelta
from tumkwe_invest.ui.dashboard import (
    InsightCard,
    Dashboard,
    StockDashboard,
    create_apple_dashboard
)


class TestInsightCard(unittest.TestCase):
    """Test the InsightCard class."""

    def setUp(self):
        """Set up test fixtures."""
        self.card = InsightCard(
            title="P/E Ratio",
            value="15.2",
            interpretation="Below industry average",
            trend="-2.3",
            trend_direction="down"
        )

    def test_initialization(self):
        """Test card initialization."""
        self.assertEqual(self.card.title, "P/E Ratio")
        self.assertEqual(self.card.value, "15.2")
        self.assertEqual(self.card.interpretation, "Below industry average")
        self.assertEqual(self.card.trend, "-2.3")
        self.assertEqual(self.card.trend_direction, "down")
        self.assertIsNone(self.card.tooltip)

    def test_add_tooltip(self):
        """Test adding tooltip to card."""
        tooltip = "Price-to-Earnings ratio compares the stock price to earnings per share."
        self.card.add_tooltip(tooltip)
        self.assertEqual(self.card.tooltip, tooltip)

    def test_to_dict(self):
        """Test converting card to dictionary."""
        tooltip = "Price-to-Earnings ratio compares the stock price to earnings per share."
        self.card.add_tooltip(tooltip)
        card_dict = self.card.to_dict()
        
        self.assertEqual(card_dict["title"], "P/E Ratio")
        self.assertEqual(card_dict["value"], "15.2")
        self.assertEqual(card_dict["interpretation"], "Below industry average")
        self.assertEqual(card_dict["trend"], "-2.3")
        self.assertEqual(card_dict["trend_direction"], "down")
        self.assertEqual(card_dict["tooltip"], tooltip)


class TestDashboard(unittest.TestCase):
    """Test the Dashboard base class."""

    def setUp(self):
        """Set up test fixtures."""
        self.dashboard = Dashboard(ticker="AAPL", company_name="Apple Inc.")
        
    def test_initialization(self):
        """Test dashboard initialization."""
        self.assertEqual(self.dashboard.ticker, "AAPL")
        self.assertEqual(self.dashboard.company_name, "Apple Inc.")
        self.assertEqual(self.dashboard.view_mode, "basic")  # Default value
        self.assertIsInstance(self.dashboard.sections, dict)
        self.assertIsInstance(self.dashboard.last_updated, datetime)

    def test_add_section(self):
        """Test adding a section to the dashboard."""
        section_id = "technical"
        title = "Technical Analysis"
        components = [
            {"type": "chart", "config": {"type": "line", "data": {}}},
            {"type": "card", "config": {"title": "RSI", "value": "55"}}
        ]
        
        self.dashboard.add_section(section_id, title, components)
        
        self.assertIn(section_id, self.dashboard.sections)
        self.assertEqual(self.dashboard.sections[section_id]["title"], title)
        self.assertEqual(self.dashboard.sections[section_id]["components"], components)

    def test_toggle_view_mode(self):
        """Test toggling view mode."""
        # Default is "basic"
        self.assertEqual(self.dashboard.view_mode, "basic")
        
        # Toggle to "advanced"
        self.dashboard.toggle_view_mode()
        self.assertEqual(self.dashboard.view_mode, "advanced")
        
        # Toggle back to "basic"
        self.dashboard.toggle_view_mode()
        self.assertEqual(self.dashboard.view_mode, "basic")

    def test_generate_dashboard_config(self):
        """Test generating dashboard configuration."""
        section_id = "price"
        title = "Price Data"
        components = [
            {"type": "chart", "config": {"type": "line", "data": {}}},
        ]
        self.dashboard.add_section(section_id, title, components)
        
        config = self.dashboard.generate_dashboard_config()
        
        self.assertEqual(config["ticker"], "AAPL")
        self.assertEqual(config["company_name"], "Apple Inc.")
        self.assertEqual(config["view_mode"], "basic")
        self.assertIn("sections", config)
        self.assertIn(section_id, config["sections"])
        self.assertIn("last_updated", config)


class TestStockDashboard(unittest.TestCase):
    """Test the StockDashboard class."""

    def setUp(self):
        """Set up test fixtures."""
        self.dashboard = StockDashboard(
            ticker="AAPL", 
            company_name="Apple Inc.",
            view_mode="basic"
        )
        
        # Set up sample price data
        self.dates = ["2023-01-01", "2023-01-02", "2023-01-03"]
        self.prices = [150.0, 152.5, 151.2]
        self.volumes = [1000000, 1200000, 950000]
        
        # Set up technical indicators
        self.technical_indicators = {
            "rsi": [45.0, 55.0, 52.0],
            "macd": [0.5, 0.7, 0.6],
            "macd_signal": [0.4, 0.5, 0.6],
            "moving_averages": {
                "MA50": [148.0, 149.0, 150.0],
                "MA200": [145.0, 146.0, 147.0]
            }
        }
        
        # Set up fundamental metrics
        self.fundamental_metrics = {
            "pe_ratio": {"value": 15.2, "industry_avg": 18.5},
            "roe": {"value": 0.25, "industry_avg": 0.18},
            "profit_margin": {"value": 0.22, "industry_avg": 0.15},
            "debt_to_equity": {"value": 0.8, "industry_avg": 1.2}
        }
        
        # Set up sentiment data
        self.sentiment_data = {
            "overall_score": 0.75,
            "summary": "Overall positive sentiment based on recent news",
            "news_items": [
                {
                    "title": "Apple Announces New Product Line",
                    "source": "Tech News",
                    "date": "2023-01-02",
                    "sentiment": 0.85,
                    "url": "https://example.com/news/1"
                }
            ],
            "integrated_score": 82
        }

    def test_initialization(self):
        """Test StockDashboard initialization."""
        self.assertEqual(self.dashboard.ticker, "AAPL")
        self.assertEqual(self.dashboard.company_name, "Apple Inc.")
        self.assertEqual(self.dashboard.view_mode, "basic")
        self.assertIsInstance(self.dashboard.price_data, dict)
        self.assertIsInstance(self.dashboard.technical_indicators, dict)
        self.assertIsInstance(self.dashboard.fundamental_metrics, dict)
        self.assertIsInstance(self.dashboard.sentiment_data, dict)

    def test_set_price_data(self):
        """Test setting price data."""
        self.dashboard.set_price_data(self.dates, self.prices, self.volumes)
        
        self.assertEqual(self.dashboard.price_data["dates"], self.dates)
        self.assertEqual(self.dashboard.price_data["prices"], self.prices)
        self.assertEqual(self.dashboard.price_data["volumes"], self.volumes)

    def test_set_technical_indicators(self):
        """Test setting technical indicators."""
        self.dashboard.set_technical_indicators(self.technical_indicators)
        
        self.assertEqual(self.dashboard.technical_indicators, self.technical_indicators)

    def test_set_fundamental_metrics(self):
        """Test setting fundamental metrics."""
        self.dashboard.set_fundamental_metrics(self.fundamental_metrics)
        
        self.assertEqual(self.dashboard.fundamental_metrics, self.fundamental_metrics)

    def test_set_sentiment_data(self):
        """Test setting sentiment data."""
        self.dashboard.set_sentiment_data(self.sentiment_data)
        
        self.assertEqual(self.dashboard.sentiment_data, self.sentiment_data)

    def test_build_price_section(self):
        """Test building price section."""
        # Set up required data
        self.dashboard.set_price_data(self.dates, self.prices, self.volumes)
        
        # Initially sections should be empty
        self.assertEqual(len(self.dashboard.sections), 0)
        
        # Build price section
        self.dashboard.build_price_section()
        
        # Check section was added
        self.assertIn("price", self.dashboard.sections)
        self.assertEqual(self.dashboard.sections["price"]["title"], "Price Information")
        
        # Check components in the section
        components = self.dashboard.sections["price"]["components"]
        self.assertEqual(len(components), 2)  # Chart and card
        self.assertEqual(components[0]["type"], "chart")
        self.assertEqual(components[1]["type"], "card")

    def test_build_technical_section_basic_view(self):
        """Test building technical analysis section in basic view."""
        # Set up required data
        self.dashboard.set_technical_indicators(self.technical_indicators)
        
        # Build technical section
        self.dashboard.build_technical_section()
        
        # Check section was added with simplified components for basic view
        self.assertIn("technical", self.dashboard.sections)
        components = self.dashboard.sections["technical"]["components"]
        
        # In basic view, we should have cards but no detailed chart
        self.assertGreaterEqual(len(components), 1)
        for component in components:
            self.assertEqual(component["type"], "card")

    def test_build_technical_section_advanced_view(self):
        """Test building technical analysis section in advanced view."""
        # Set up required data and switch to advanced view
        self.dashboard.set_technical_indicators(self.technical_indicators)
        self.dashboard.set_price_data(self.dates, self.prices, self.volumes)
        self.dashboard.view_mode = "advanced"
        
        # Build technical section
        self.dashboard.build_technical_section()
        
        # Check section was added with detailed components for advanced view
        self.assertIn("technical", self.dashboard.sections)
        components = self.dashboard.sections["technical"]["components"]
        
        # In advanced view, we should have a chart and cards
        self.assertGreaterEqual(len(components), 1)
        self.assertEqual(components[0]["type"], "chart")

    def test_build_dashboard(self):
        """Test building the complete dashboard."""
        # Set up all required data
        self.dashboard.set_price_data(self.dates, self.prices, self.volumes)
        self.dashboard.set_technical_indicators(self.technical_indicators)
        self.dashboard.set_fundamental_metrics(self.fundamental_metrics)
        self.dashboard.set_sentiment_data(self.sentiment_data)
        
        # Build dashboard
        config = self.dashboard.build_dashboard()
        
        # Check complete dashboard structure
        self.assertEqual(config["ticker"], "AAPL")
        self.assertEqual(config["company_name"], "Apple Inc.")
        self.assertEqual(config["view_mode"], "basic")
        
        # Should have these sections
        self.assertIn("price", config["sections"])
        self.assertIn("technical", config["sections"])
        self.assertIn("fundamental", config["sections"])
        self.assertIn("sentiment", config["sections"])
        
        # In basic view, shouldn't have integrated section
        self.assertNotIn("integrated", config["sections"])
        
        # Switch to advanced view and rebuild
        self.dashboard.view_mode = "advanced"
        config = self.dashboard.build_dashboard()
        
        # Now should have integrated section
        self.assertIn("integrated", config["sections"])

    def test_calculate_technical_health(self):
        """Test calculating technical health."""
        self.dashboard.set_technical_indicators(self.technical_indicators)
        health = self.dashboard._calculate_technical_health()
        
        # Check health structure
        self.assertIn("status", health)
        self.assertIn("interpretation", health)
        self.assertIn("trend_direction", health)
        
        # Values should be strings
        self.assertIsInstance(health["status"], str)
        self.assertIsInstance(health["interpretation"], str)
        self.assertIsInstance(health["trend_direction"], str)

    def test_calculate_financial_health(self):
        """Test calculating financial health."""
        self.dashboard.set_fundamental_metrics(self.fundamental_metrics)
        health = self.dashboard._calculate_financial_health()
        
        # Check health structure
        self.assertIn("status", health)
        self.assertIn("interpretation", health)
        self.assertIn("trend_direction", health)
        
        # Values should be strings
        self.assertIsInstance(health["status"], str)
        self.assertIsInstance(health["interpretation"], str)
        self.assertIsInstance(health["trend_direction"], str)


class TestAppleDashboardCreation(unittest.TestCase):
    """Test the create_apple_dashboard function."""
    
    def test_create_apple_dashboard_basic(self):
        """Test creating an Apple dashboard with basic view."""
        dashboard = create_apple_dashboard("basic")
        
        self.assertEqual(dashboard["ticker"], "AAPL")
        self.assertEqual(dashboard["company_name"], "Apple Inc.")
        self.assertEqual(dashboard["view_mode"], "basic")
        
        # Should have basic sections
        self.assertIn("price", dashboard["sections"])
        self.assertIn("technical", dashboard["sections"])
        self.assertIn("fundamental", dashboard["sections"])
        self.assertIn("sentiment", dashboard["sections"])
        
        # Should not have advanced section
        self.assertNotIn("integrated", dashboard["sections"])
        
    def test_create_apple_dashboard_advanced(self):
        """Test creating an Apple dashboard with advanced view."""
        dashboard = create_apple_dashboard("advanced")
        
        self.assertEqual(dashboard["ticker"], "AAPL")
        self.assertEqual(dashboard["company_name"], "Apple Inc.")
        self.assertEqual(dashboard["view_mode"], "advanced")
        
        # Should have all sections including advanced ones
        self.assertIn("price", dashboard["sections"])
        self.assertIn("technical", dashboard["sections"])
        self.assertIn("fundamental", dashboard["sections"])
        self.assertIn("sentiment", dashboard["sections"])
        self.assertIn("integrated", dashboard["sections"])


if __name__ == "__main__":
    unittest.main()
