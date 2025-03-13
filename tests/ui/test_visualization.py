"""Test cases for the visualization module."""

import unittest
import json
from tumkwe_invest.ui.visualization import (
    StockChart,
    ComparisonChart,
    create_stock_price_chart,
    create_technical_indicators_chart,
    create_fundamental_comparison_chart,
    create_sentiment_gauge
)


class TestStockChart(unittest.TestCase):
    """Test the StockChart class."""

    def setUp(self):
        """Set up test fixtures."""
        self.dates = ["2023-01-01", "2023-01-02", "2023-01-03"]
        self.prices = [150.0, 152.5, 151.2]
        self.chart = StockChart(chart_type="line", theme="light")

    def test_initialization(self):
        """Test chart initialization."""
        self.assertEqual(self.chart.chart_type, "line")
        self.assertEqual(self.chart.theme, "light")
        self.assertIsInstance(self.chart.data, dict)
        self.assertIsInstance(self.chart.options, dict)

    def test_add_price_data(self):
        """Test adding price data to the chart."""
        self.chart.add_price_data(self.dates, self.prices, label="Test Stock")
        
        # Check that data was added correctly
        self.assertEqual(self.chart.data["labels"], self.dates)
        self.assertEqual(len(self.chart.data["datasets"]), 1)
        self.assertEqual(self.chart.data["datasets"][0]["data"], self.prices)
        self.assertEqual(self.chart.data["datasets"][0]["label"], "Test Stock")

    def test_add_trend_indicators(self):
        """Test adding trend indicators to the chart."""
        # Set up price data first
        self.chart.add_price_data(self.dates, self.prices)
        
        # Add trend indicators
        indicators = {
            "MA50": [148.0, 149.0, 150.0],
            "MA200": [145.0, 146.0, 147.0]
        }
        self.chart.add_trend_indicators(indicators)
        
        # Check that indicators were added correctly
        self.assertEqual(len(self.chart.data["datasets"]), 3)  # Price data + 2 indicators
        self.assertEqual(self.chart.data["datasets"][1]["label"], "MA50")
        self.assertEqual(self.chart.data["datasets"][1]["data"], indicators["MA50"])
        self.assertEqual(self.chart.data["datasets"][2]["label"], "MA200")
        self.assertEqual(self.chart.data["datasets"][2]["data"], indicators["MA200"])

    def test_generate_config(self):
        """Test generating chart configuration."""
        self.chart.add_price_data(self.dates, self.prices)
        config = self.chart.generate_config()
        
        # Check that configuration is correctly structured
        self.assertEqual(config["type"], "line")
        self.assertIn("data", config)
        self.assertIn("options", config)
        self.assertEqual(config["data"]["labels"], self.dates)

    def test_to_json(self):
        """Test converting chart to JSON."""
        self.chart.add_price_data(self.dates, self.prices)
        json_str = self.chart.to_json()
        
        # Check that JSON is valid
        parsed = json.loads(json_str)
        self.assertEqual(parsed["type"], "line")
        self.assertEqual(parsed["data"]["labels"], self.dates)


class TestComparisonChart(unittest.TestCase):
    """Test the ComparisonChart class."""

    def setUp(self):
        """Set up test fixtures."""
        self.chart = ComparisonChart(chart_type="bar")
        self.labels = ["P/E", "ROE", "Debt/Equity"]
        self.datasets = [
            {
                "label": "Company",
                "data": [15.2, 0.22, 0.8],
                "backgroundColor": "rgba(66, 133, 244, 0.7)"
            },
            {
                "label": "Industry",
                "data": [18.5, 0.18, 1.2],
                "backgroundColor": "rgba(251, 188, 5, 0.7)"
            }
        ]

    def test_initialization(self):
        """Test chart initialization."""
        self.assertEqual(self.chart.chart_type, "bar")
        self.assertIsInstance(self.chart.data, dict)
        self.assertIsInstance(self.chart.options, dict)

    def test_add_comparison_data(self):
        """Test adding comparison data to the chart."""
        self.chart.add_comparison_data(self.labels, self.datasets)
        
        # Check that data was added correctly
        self.assertEqual(self.chart.data["labels"], self.labels)
        self.assertEqual(self.chart.data["datasets"], self.datasets)

    def test_generate_config(self):
        """Test generating chart configuration."""
        self.chart.add_comparison_data(self.labels, self.datasets)
        config = self.chart.generate_config()
        
        # Check that configuration is correctly structured
        self.assertEqual(config["type"], "bar")
        self.assertIn("data", config)
        self.assertIn("options", config)
        self.assertEqual(config["data"]["labels"], self.labels)
        self.assertEqual(config["data"]["datasets"], self.datasets)


class TestChartFunctions(unittest.TestCase):
    """Test the chart creation functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.dates = ["2023-01-01", "2023-01-02", "2023-01-03"]
        self.prices = [150.0, 152.5, 151.2]
        self.volumes = [1000000, 1200000, 950000]
        self.moving_averages = {
            "MA50": [148.0, 149.0, 150.0],
            "MA200": [145.0, 146.0, 147.0]
        }
        self.indicators = {
            "rsi": [45.0, 55.0, 52.0],
            "macd": [0.5, 0.7, 0.6],
            "macd_signal": [0.4, 0.5, 0.6]
        }

    def test_create_stock_price_chart(self):
        """Test creating stock price chart."""
        chart = create_stock_price_chart(self.dates, self.prices, 
                                        self.moving_averages, self.volumes)
        
        # Check chart structure
        self.assertEqual(chart["type"], "line")
        self.assertEqual(chart["data"]["labels"], self.dates)
        # First dataset should be stock price
        self.assertEqual(chart["data"]["datasets"][0]["data"], self.prices)
        # Next datasets should be moving averages
        self.assertEqual(chart["data"]["datasets"][1]["data"], self.moving_averages["MA50"])
        self.assertEqual(chart["data"]["datasets"][2]["data"], self.moving_averages["MA200"])

    def test_create_technical_indicators_chart(self):
        """Test creating technical indicators chart."""
        chart = create_technical_indicators_chart(self.dates, self.indicators)
        
        self.assertEqual(chart["type"], "line")
        self.assertEqual(chart["data"]["labels"], self.dates)
        # Should have datasets for each indicator
        self.assertEqual(len(chart["data"]["datasets"]), len(self.indicators))

    def test_create_fundamental_comparison_chart(self):
        """Test creating fundamental comparison chart."""
        metrics = ["P/E", "ROE", "Debt/Equity"]
        stock_values = [15.2, 0.22, 0.8]
        benchmark_values = [18.5, 0.18, 1.2]
        industry_values = [17.0, 0.2, 1.0]
        
        chart = create_fundamental_comparison_chart(metrics, stock_values, 
                                                   benchmark_values, industry_values)
        
        self.assertEqual(chart["type"], "bar")
        self.assertEqual(chart["data"]["labels"], metrics)
        # Should have datasets for stock, benchmark, and industry
        self.assertEqual(len(chart["data"]["datasets"]), 3)
        self.assertEqual(chart["data"]["datasets"][0]["data"], stock_values)
        self.assertEqual(chart["data"]["datasets"][1]["data"], benchmark_values)
        self.assertEqual(chart["data"]["datasets"][2]["data"], industry_values)

    def test_create_sentiment_gauge(self):
        """Test creating sentiment gauge chart."""
        score = 0.75
        gauge = create_sentiment_gauge(score)
        
        self.assertEqual(gauge["type"], "gauge")
        self.assertEqual(gauge["data"]["datasets"][0]["value"], score)


if __name__ == "__main__":
    unittest.main()
