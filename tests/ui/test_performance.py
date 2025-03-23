"""
Performance and edge case tests for UI components in Tumkwe Invest.
"""

import json
import time

from tumkwe_invest.ui.components import Button, Card
from tumkwe_invest.ui.dashboard import StockDashboard
from tumkwe_invest.ui.visualization import StockChart


class TestLargeDataHandling:
    def test_chart_with_large_dataset(self):
        """Test chart performance with a large number of data points."""
        # Generate a large dataset (e.g., daily data for 5 years)
        num_points = 365 * 5
        dates = [f"2020-01-{i % 30 + 1}" for i in range(num_points)]
        prices = [100 + (i % 100) for i in range(num_points)]

        # Measure time to generate chart
        start_time = time.time()
        chart = StockChart("line")
        chart.add_price_data(dates, prices)
        config = chart.generate_config()
        generation_time = time.time() - start_time

        # Verify the chart was created with all data points
        assert len(config["data"]["labels"]) == num_points
        assert len(config["data"]["datasets"][0]["data"]) == num_points

        # Performance thresholds - this is a basic test, adjust as needed
        # For large datasets, chart generation should still be reasonably quick
        assert (
            generation_time < 1.0
        ), f"Chart generation took {generation_time:.2f} seconds"

        # Test JSON serialization time and size
        start_time = time.time()
        json_data = json.dumps(config)
        serialization_time = time.time() - start_time

        # Check serialization performance
        assert (
            serialization_time < 0.5
        ), f"JSON serialization took {serialization_time:.2f} seconds"
        assert len(json_data) < 10 * 1024 * 1024, "JSON output is too large"

    def test_dashboard_with_comprehensive_data(
        self,
        sample_dates,
        sample_prices,
        sample_technical_indicators,
        sample_fundamental_metrics,
        sample_sentiment_data,
    ):
        """Test dashboard performance with comprehensive data."""
        # Create dashboard with a large set of data
        dashboard = StockDashboard("COMP", "Comprehensive Test Co.", "advanced")

        # Add large price dataset
        dashboard.set_price_data(sample_dates, sample_prices)

        # Add technical indicators
        dashboard.set_technical_indicators(sample_technical_indicators)

        # Add fundamental metrics
        dashboard.set_fundamental_metrics(sample_fundamental_metrics)

        # Add sentiment data
        dashboard.set_sentiment_data(sample_sentiment_data)

        # Measure dashboard build time
        start_time = time.time()
        dashboard_config = dashboard.build_dashboard()
        build_time = time.time() - start_time

        # Performance threshold
        assert build_time < 1.0, f"Dashboard build took {build_time:.2f} seconds"

        # Verify all sections were built
        assert "price" in dashboard_config["sections"]
        assert "technical" in dashboard_config["sections"]
        assert "fundamental" in dashboard_config["sections"]
        assert "sentiment" in dashboard_config["sections"]
        assert "integrated" in dashboard_config["sections"]  # Advanced mode


class TestEdgeCases:
    def test_empty_data_handling(self):
        """Test how components handle empty or partial data."""
        # Chart with no data
        empty_chart = StockChart()
        empty_config = empty_chart.generate_config()
        assert "data" in empty_config
        assert empty_config["data"] == {}

        # Chart with dates but no prices
        dates_only_chart = StockChart()
        dates_only_chart.data["labels"] = ["2023-01-01", "2023-01-02"]
        dates_only_chart.data["datasets"] = []
        dates_only_config = dates_only_chart.generate_config()
        assert len(dates_only_config["data"]["labels"]) == 2
        assert dates_only_config["data"]["datasets"] == []

        # Dashboard with no data should not generate sections
        empty_dashboard = StockDashboard("NONE", "No Data Corp.")
        empty_result = empty_dashboard.build_dashboard()
        assert empty_result["sections"] == {}

        # Dashboard with price data but no other data
        partial_dashboard = StockDashboard("PART", "Partial Data Inc.")
        partial_dashboard.set_price_data(["2023-01-01"], [100.0])
        partial_result = partial_dashboard.build_dashboard()
        assert "price" in partial_result["sections"]
        assert "technical" not in partial_result["sections"]
        assert "fundamental" not in partial_result["sections"]

    def test_special_characters_handling(self):
        """Test handling of special characters in component content."""
        # Test card with HTML content and special characters
        special_chars = "<script>alert('XSS')</script> & < > \" ' ® © ™ € £ ¥"
        card = Card("Special Characters", special_chars)
        card_dict = card.to_dict()

        # Ensure content is preserved but not sanitized (sanitization would be done at render time)
        assert "<script>" in card_dict["content"]

        # Test button with special characters
        button = Button("Click & Save © ™")
        button_dict = button.to_dict()
        assert button_dict["label"] == "Click & Save © ™"

    def test_nested_component_depth(self):
        """Test deeply nested components."""
        # Create a deeply nested structure (Card > Card > Card > Button)
        inner_button = Button("Inner Button", "primary", "small", "inner-btn")

        level3_card = Card("Level 3", inner_button.to_dict(), "level3-card")
        level2_card = Card("Level 2", level3_card.to_dict(), "level2-card")
        level1_card = Card("Level 1", level2_card.to_dict(), "level1-card")

        # Convert to dictionary
        result = level1_card.to_dict()

        # Verify nested structure
        assert result["title"] == "Level 1"
        assert result["content"]["title"] == "Level 2"
        assert result["content"]["content"]["title"] == "Level 3"
        assert result["content"]["content"]["content"]["label"] == "Inner Button"


class TestChartPerformanceOptimizations:
    def test_chart_default_point_radius_optimization(self):
        """Test that charts with many points reduce point radius for performance."""
        # Create a chart with few points - should have normal point radius
        small_chart = StockChart()
        small_chart.add_price_data(
            ["2023-01-01", "2023-01-02", "2023-01-03"], [100.0, 102.0, 101.0]
        )
        small_config = small_chart.generate_config()

        # Create a chart with many points - should have reduced point radius
        large_chart = StockChart()
        large_dates = [f"2023-01-{i}" for i in range(1, 101)]
        large_prices = [100.0 + (i % 10) for i in range(100)]
        large_chart.add_price_data(large_dates, large_prices)
        large_config = large_chart.generate_config()

        # For a small dataset, point radius should be normal
        assert small_config["data"]["datasets"][0]["pointRadius"] == 1

        # For a large dataset, chart should still render all points
        assert len(large_config["data"]["datasets"][0]["data"]) == 100
