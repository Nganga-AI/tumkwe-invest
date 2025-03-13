# Tumkwe Invest UI Module

This module provides components for creating intuitive, accessible interfaces for users with varying levels of financial expertise.

## Overview

The UI module consists of:

- **visualization.py**: Chart and graph components using Chart.js/D3.js
- **dashboard.py**: Dashboard layouts for displaying insights
- **components.py**: Reusable UI elements (cards, buttons, tooltips)
- **utils.py**: Helper functions for formatting and accessibility

## Using the UI Module

### Basic Dashboard Setup

```python
from tumkwe_invest.ui.dashboard import StockDashboard

# Create a dashboard (basic view by default)
dashboard = StockDashboard(
    ticker="AAPL",
    company_name="Apple Inc."
)

# Set price data
dashboard.set_price_data(
    dates=['2023-01-01', '2023-01-02', '2023-01-03'],
    prices=[150.5, 152.3, 148.7],
    volumes=[5000000, 6200000, 4800000]
)

# Generate dashboard configuration
config = dashboard.build_dashboard()
```

### Integration with Data Collection Module

```python
from tumkwe_invest.datacollection.collectors.yahoo_finance import YahooFinanceCollector
from tumkwe_invest.ui.dashboard import StockDashboard

# Collect data
collector = YahooFinanceCollector()
stock_data = collector.get_historical_data("AAPL", period="1mo")

# Create dashboard
dashboard = StockDashboard("AAPL", "Apple Inc.")
dashboard.set_price_data(
    dates=stock_data["dates"],
    prices=stock_data["close_prices"],
    volumes=stock_data["volumes"]
)

# Build and output dashboard
config = dashboard.build_dashboard()
```

### Integration with Analysis Modules

```python
from tumkwe_invest.datacollection.collectors.yahoo_finance import YahooFinanceCollector
from tumkwe_invest.data_analysis.technical_analysis import calculate_technical_indicators
from tumkwe_invest.data_analysis.fundamental_analysis import calculate_fundamental_metrics
from tumkwe_invest.data_analysis.sentiment_analysis import analyze_sentiment
from tumkwe_invest.ui.dashboard import StockDashboard

# Collect data
collector = YahooFinanceCollector()
stock_data = collector.get_historical_data("AAPL", period="6mo")
news_data = collector.get_news("AAPL")

# Perform analysis
technical_indicators = calculate_technical_indicators(stock_data)
fundamental_metrics = calculate_fundamental_metrics("AAPL")
sentiment_results = analyze_sentiment("AAPL", news_data)

# Create dashboard with all data
dashboard = StockDashboard("AAPL", "Apple Inc.", view_mode="advanced")
dashboard.set_price_data(
    stock_data["dates"], 
    stock_data["close_prices"],
    stock_data["volumes"]
)
dashboard.set_technical_indicators(technical_indicators)
dashboard.set_fundamental_metrics(fundamental_metrics)
dashboard.set_sentiment_data(sentiment_results)

# Build dashboard
dashboard_config = dashboard.build_dashboard()
```

### Creating Custom Visualizations

```python
from tumkwe_invest.ui.visualization import StockChart

# Create a custom chart
chart = StockChart(chart_type="line", theme="dark")
chart.add_price_data(
    dates=['2023-01-01', '2023-01-02', '2023-01-03'],
    prices=[150.5, 152.3, 148.7],
    label="AAPL"
)

# Add technical indicators
chart.add_trend_indicators({
    "MA50": [148.2, 149.1, 149.8],
    "MA200": [145.3, 145.5, 145.8]
})

# Get chart configuration for rendering
chart_config = chart.generate_config()
```

### Using UI Components

```python
from tumkwe_invest.ui.components import Card, Button, Tooltip, create_metric_card

# Create a metric card
card_config = create_metric_card(
    title="Revenue Growth",
    value="15.3%",
    description="Year-over-year increase",
    trend="+2.1%",
    trend_direction="up",
    tooltip="Revenue growth measures the increase in a company's sales over time."
)

# Create a custom button
button = Button(
    label="View Details",
    variant="primary",
    component_id="details-btn"
)
button.on_event("click", "showDetails()")
button_config = button.to_dict()
```

### Formatting with Utilities

```python
from tumkwe_invest.ui.utils import (
    format_currency, format_percent, get_trend_color, simplify_large_number
)

# Format values for display
price = format_currency(1234.56)  # "$1,234.56"
growth = format_percent(0.0753, include_sign=True)  # "+7.53%"
revenue = simplify_large_number(1234567890)  # "1.2B"

# Get appropriate color for a trend
color = get_trend_color(0.15)  # Returns a green hex color
```

## Supporting Different User Expertise Levels

The UI module is designed to accommodate users with varying levels of financial expertise:

### Basic View

- Simplified terminology and visualizations
- Focus on key metrics with plain language explanations
- Color-coded trends for intuitive understanding

### Advanced View

- Comprehensive technical and fundamental indicators
- Detailed charts with multiple data points
- In-depth explanations and industry comparisons

Toggle between views using the Dashboard's `toggle_view_mode()` method or initialize with your preferred mode:

```python
# Create a dashboard with advanced view
dashboard = StockDashboard("AAPL", "Apple Inc.", view_mode="advanced")

# Or toggle between views
dashboard.toggle_view_mode()  # Switch from basic to advanced or vice versa
```

## Accessibility Features

The UI is designed with accessibility in mind:

- Tooltips provide explanations for financial terms
- Color contrast meets WCAG guidelines
- ARIA attributes for screen readers
- Keyboard shortcuts for navigation

Use `AccessibilityUtils` from `utils.py` for additional accessibility features.
