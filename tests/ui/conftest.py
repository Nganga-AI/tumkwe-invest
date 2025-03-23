"""
Pytest fixtures for UI component tests.
"""

from datetime import datetime, timedelta

import pytest


@pytest.fixture
def sample_dates():
    """Fixture providing sample dates for charts and testing."""
    today = datetime.now()
    return [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30, 0, -1)]


@pytest.fixture
def sample_prices():
    """Fixture providing sample price data for testing."""
    base_price = 100.0
    prices = []
    for i in range(30):
        # Create some realistic price movements
        change = (i % 5 - 2) * 0.5  # Create some cyclical patterns
        random_factor = (i % 7) * 0.3  # Add some randomness
        price = base_price + change + random_factor
        prices.append(price)
    return prices


@pytest.fixture
def sample_technical_indicators(sample_prices):
    """Fixture providing sample technical indicators for testing."""
    # Generate some plausible technical indicators based on the sample prices
    rsi = []
    macd = []
    macd_signal = []
    ma_50 = []

    # Simple mock calculations
    for i, price in enumerate(sample_prices):
        # RSI between 30 and 70
        rsi_val = 30 + (price % 40)
        rsi.append(rsi_val)

        # MACD values
        macd_val = (price - 100) * 0.01
        macd.append(macd_val)

        # MACD signal slightly lagging
        if i > 0:
            macd_signal.append(macd[i - 1])
        else:
            macd_signal.append(0)

        # 50-day MA slightly below price
        ma_50.append(price * 0.98)

    return {
        "rsi": rsi,
        "macd": macd,
        "macd_signal": macd_signal,
        "moving_averages": {"MA50": ma_50},
    }


@pytest.fixture
def sample_fundamental_metrics():
    """Fixture providing sample fundamental metrics for testing."""
    return {
        "pe_ratio": {"value": 25.6, "industry_avg": 22.1},
        "roe": {"value": 0.35, "industry_avg": 0.28},
        "roa": {"value": 0.22, "industry_avg": 0.18},
        "profit_margin": {"value": 0.21, "industry_avg": 0.17},
        "debt_to_equity": {"value": 1.2, "industry_avg": 1.5},
        "current_ratio": {"value": 1.8, "industry_avg": 1.6},
    }


@pytest.fixture
def sample_sentiment_data():
    """Fixture providing sample sentiment data for testing."""
    return {
        "overall_score": 0.65,
        "summary": "Recent positive news and analyst upgrades contribute to bullish sentiment",
        "news_items": [
            {
                "title": "Company Reports Strong Q2 Results",
                "source": "Financial Times",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "sentiment": 0.8,
                "url": "https://example.com/news1",
            },
            {
                "title": "New Product Launch Expected To Boost Sales",
                "source": "Tech Today",
                "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                "sentiment": 0.7,
                "url": "https://example.com/news2",
            },
            {
                "title": "Industry Facing Supply Chain Challenges",
                "source": "Wall Street Journal",
                "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                "sentiment": -0.3,
                "url": "https://example.com/news3",
            },
        ],
        "integrated_score": 72,
    }


@pytest.fixture
def sample_ui_component():
    """Fixture providing a basic UIComponent for testing."""
    from tumkwe_invest.ui.components import UIComponent

    component = UIComponent("test-component")
    component.add_class("test-class")
    component.set_attribute("data-test", "value")
    component.on_event("click", "handleClick()")
    return component


@pytest.fixture
def sample_card():
    """Fixture providing a Card component for testing."""
    from tumkwe_invest.ui.components import Card

    card = Card(
        title="Sample Card",
        content={"value": "Content value", "description": "Content description"},
        component_id="sample-card",
    )
    card.add_class("custom-card")
    card.set_footer("Card footer")
    card.add_header_action({"icon": "info", "handler": "showInfo()"})
    return card


@pytest.fixture
def sample_stock_chart():
    """Fixture providing a configured StockChart for testing."""
    from tumkwe_invest.ui.visualization import StockChart

    chart = StockChart("line", "light")
    dates = ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"]
    prices = [100.0, 102.5, 101.8, 103.2, 105.0]
    chart.add_price_data(dates, prices, "Stock Price")
    chart.add_trend_indicators(
        {
            "MA50": [99.0, 100.5, 101.0, 102.0, 103.0],
            "RSI": [45.0, 52.0, 48.0, 55.0, 60.0],
        }
    )
    return chart


@pytest.fixture
def sample_dashboard():
    """Fixture providing a configured StockDashboard for testing."""
    from tumkwe_invest.ui.dashboard import StockDashboard

    dashboard = StockDashboard("TSLA", "Tesla, Inc.", "basic")

    # Add sample data
    dates = ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"]
    prices = [180.0, 185.5, 182.8, 188.2, 190.0]
    volumes = [1000000, 1200000, 900000, 1500000, 1300000]

    dashboard.set_price_data(dates, prices, volumes)

    dashboard.set_technical_indicators(
        {
            "rsi": [55, 60, 48, 65, 70],
            "macd": [0.5, 0.6, 0.4, 0.7, 0.8],
            "macd_signal": [0.4, 0.5, 0.5, 0.6, 0.7],
            "moving_averages": {
                "MA50": [175, 178, 180, 183, 185],
                "MA200": [160, 162, 164, 166, 168],
            },
        }
    )

    dashboard.set_fundamental_metrics(
        {
            "pe_ratio": {"value": 60.5, "industry_avg": 40.2},
            "roe": {"value": 0.25, "industry_avg": 0.20},
            "profit_margin": {"value": 0.15, "industry_avg": 0.12},
            "debt_to_equity": {"value": 0.8, "industry_avg": 1.2},
        }
    )

    dashboard.set_sentiment_data(
        {
            "overall_score": 0.72,
            "summary": "Positive sentiment driven by strong delivery numbers and expansion plans",
            "news_items": [
                {
                    "title": "Tesla Reports Record Deliveries",
                    "source": "Financial Times",
                    "date": dates[0],
                    "sentiment": 0.9,
                    "url": "https://example.com/tesla-news1",
                }
            ],
            "integrated_score": 80,
        }
    )

    return dashboard
