"""
Visualization components for Tumkwe Invest.

This module provides functions to create interactive charts and visualizations
using libraries like Chart.js or D3.js.
"""

import json
from typing import Any, Dict, List, Optional


class StockChart:
    """Class for generating stock price and trend visualizations."""

    def __init__(self, chart_type: str = "line", theme: str = "light"):
        """
        Initialize a stock chart visualization.

        Args:
            chart_type: Type of chart ('line', 'candlestick', 'area', etc.)
            theme: Visual theme ('light', 'dark', 'high_contrast')
        """
        self.chart_type = chart_type
        self.theme = theme
        self.data = {}
        self.options = self._get_default_options()

    def _get_default_options(self) -> Dict[str, Any]:
        """Return default chart options based on theme and type."""
        colors = {
            "light": {
                "positive": "#34A853",  # Green for positive trends
                "negative": "#EA4335",  # Red for negative trends
                "neutral": "#4285F4",  # Blue for neutral information
                "background": "#FFFFFF",
                "text": "#202124",
            },
            "dark": {
                "positive": "#00C853",
                "negative": "#FF5252",
                "neutral": "#448AFF",
                "background": "#121212",
                "text": "#FFFFFF",
            },
            "high_contrast": {
                "positive": "#00E676",
                "negative": "#FF1744",
                "neutral": "#2979FF",
                "background": "#000000",
                "text": "#FFFFFF",
            },
        }

        options = {
            "colors": colors.get(self.theme, colors["light"]),
            "responsive": True,
            "maintainAspectRatio": False,
            "tooltip": {"enabled": True, "mode": "index", "intersect": False},
            "legend": {"display": True, "position": "top"},
        }

        return options

    def add_price_data(
        self, dates: List[str], prices: List[float], label: str = "Price"
    ) -> None:
        """
        Add price data to the chart.

        Args:
            dates: List of date strings
            prices: List of price values
            label: Label for the dataset
        """
        self.data.update(
            {
                "labels": dates,
                "datasets": [
                    {
                        "label": label,
                        "data": prices,
                        "borderColor": self.options["colors"]["neutral"],
                        "backgroundColor": self._adjust_opacity(
                            self.options["colors"]["neutral"], 0.2
                        ),
                        "borderWidth": 2,
                        "pointRadius": 1,
                        "pointHoverRadius": 5,
                        "fill": self.chart_type == "area",
                    }
                ],
            }
        )

    def add_trend_indicators(
        self,
        indicators: Dict[str, List[float]],
        colors: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Add technical indicators or trend lines to the chart.

        Args:
            indicators: Dictionary mapping indicator names to data points
            colors: Optional custom colors for each indicator
        """
        if "datasets" not in self.data:
            self.data["datasets"] = []

        if not colors:
            colors = {}

        for idx, (name, values) in enumerate(indicators.items()):
            color = colors.get(name, self._get_color_by_index(idx))
            self.data["datasets"].append(
                {
                    "label": name,
                    "data": values,
                    "borderColor": color,
                    "backgroundColor": "transparent",
                    "borderWidth": 1.5,
                    "pointRadius": 0,
                    "pointHoverRadius": 3,
                    "fill": False,
                }
            )

    def _get_color_by_index(self, index: int) -> str:
        """Generate color based on index for multiple indicators."""
        colors = [
            "#4285F4",  # Blue
            "#EA4335",  # Red
            "#FBBC05",  # Yellow
            "#34A853",  # Green
            "#8F00FF",  # Purple
            "#FF6D01",  # Orange
            "#46BFBD",  # Teal
            "#F7464A",  # Crimson
        ]
        return colors[index % len(colors)]

    def _adjust_opacity(self, hex_color: str, opacity: float) -> str:
        """Convert hex color to rgba with opacity."""
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r}, {g}, {b}, {opacity})"

    def generate_config(self) -> Dict[str, Any]:
        """Generate the full chart configuration."""
        return {"type": self.chart_type, "data": self.data, "options": self.options}

    def to_json(self) -> str:
        """Convert chart configuration to JSON for web rendering."""
        return json.dumps(self.generate_config())


class ComparisonChart:
    """Class for creating comparative visualizations."""

    def __init__(self, chart_type: str = "bar"):
        """
        Initialize a comparison chart.

        Args:
            chart_type: Type of chart ('bar', 'radar', 'polar')
        """
        self.chart_type = chart_type
        self.data = {}
        self.options = {
            "responsive": True,
            "scales": {"y": {"beginAtZero": False}},
            "plugins": {
                "tooltip": {
                    "callbacks": {
                        "label": "function(context) { return context.dataset.label + ': ' + context.raw; }"
                    }
                }
            },
        }

    def add_comparison_data(self, labels: List[str], datasets: List[Dict]) -> None:
        """
        Add comparison data to the chart.

        Args:
            labels: Category/metric labels
            datasets: List of dataset objects with values to compare
        """
        self.data = {"labels": labels, "datasets": datasets}

    def generate_config(self) -> Dict[str, Any]:
        """Generate the full chart configuration."""
        return {"type": self.chart_type, "data": self.data, "options": self.options}

    def to_json(self) -> str:
        """Convert chart configuration to JSON for web rendering."""
        return json.dumps(self.generate_config())


def create_stock_price_chart(
    dates: List[str],
    prices: List[float],
    moving_averages: Optional[Dict[str, List[float]]] = None,
    volume: Optional[List[int]] = None,
    theme: str = "light",
) -> Dict[str, Any]:
    """
    Create a comprehensive stock price chart with optional indicators.

    Args:
        dates: List of date strings
        prices: List of price values
        moving_averages: Optional dictionary of moving averages
        volume: Optional volume data
        theme: Visual theme

    Returns:
        Chart configuration dictionary
    """
    chart = StockChart(chart_type="line", theme=theme)
    chart.add_price_data(dates, prices, "Stock Price")

    if moving_averages:
        chart.add_trend_indicators(moving_averages)

    if volume:
        # Add volume as a separate panel/chart
        pass

    return chart.generate_config()


def create_technical_indicators_chart(
    dates: List[str], indicators: Dict[str, List[float]], theme: str = "light"
) -> Dict[str, Any]:
    """
    Create a chart displaying technical indicators.

    Args:
        dates: List of date strings
        indicators: Dictionary mapping indicator names to data points
        theme: Visual theme

    Returns:
        Chart configuration dictionary
    """
    chart = StockChart(chart_type="line", theme=theme)

    # Use empty prices as placeholder to set up chart structure
    empty_prices = [None] * len(dates)
    chart.add_price_data(dates, empty_prices, "")

    # Remove the empty dataset
    chart.data["datasets"] = []

    # Add all indicators
    chart.add_trend_indicators(indicators)

    return chart.generate_config()


def create_fundamental_comparison_chart(
    metrics: List[str],
    stock_values: List[float],
    benchmark_values: List[float],
    industry_values: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """
    Create a chart comparing fundamental metrics with benchmarks.

    Args:
        metrics: List of metric names
        stock_values: Values for the analyzed stock
        benchmark_values: Benchmark/index values
        industry_values: Optional industry average values

    Returns:
        Chart configuration dictionary
    """
    chart = ComparisonChart("bar")

    datasets = [
        {
            "label": "Stock",
            "data": stock_values,
            "backgroundColor": "rgba(66, 133, 244, 0.7)",
        },
        {
            "label": "Benchmark",
            "data": benchmark_values,
            "backgroundColor": "rgba(251, 188, 5, 0.7)",
        },
    ]

    if industry_values:
        datasets.append(
            {
                "label": "Industry Average",
                "data": industry_values,
                "backgroundColor": "rgba(52, 168, 83, 0.7)",
            }
        )

    chart.add_comparison_data(metrics, datasets)

    return chart.generate_config()


def create_sentiment_gauge(
    score: float, min_value: float = -1.0, max_value: float = 1.0
) -> Dict[str, Any]:
    """
    Create a gauge chart to display sentiment score.

    Args:
        score: Sentiment score (typically -1 to 1)
        min_value: Minimum value on scale
        max_value: Maximum value on scale

    Returns:
        Gauge chart configuration
    """
    # Define colors for different sentiment ranges
    colors = {
        "very_negative": "#B71C1C",  # Dark red
        "negative": "#F44336",  # Red
        "neutral": "#FFC107",  # Amber/Yellow
        "positive": "#4CAF50",  # Green
        "very_positive": "#1B5E20",  # Dark green
    }

    # Map score to a color
    color = colors["neutral"]
    if score < -0.6:
        color = colors["very_negative"]
    elif score < -0.2:
        color = colors["negative"]
    elif score > 0.6:
        color = colors["very_positive"]
    elif score > 0.2:
        color = colors["positive"]

    gauge_config = {
        "type": "gauge",
        "data": {
            "datasets": [
                {
                    "value": score,
                    "minValue": min_value,
                    "maxValue": max_value,
                    "backgroundColor": color,
                    "borderWidth": 0,
                }
            ]
        },
        "options": {
            "needle": {
                "radiusPercentage": 2,
                "widthPercentage": 3.2,
                "lengthPercentage": 80,
                "color": "#000000",
            },
            "valueLabel": {
                "display": True,
                "formatter": "function(value) { return value.toFixed(2); }",
            },
            "responsive": True,
        },
    }

    return gauge_config
