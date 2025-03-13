"""Test fixtures for UI module tests."""

import pytest
from datetime import datetime, timedelta


@pytest.fixture
def sample_dates():
    """Sample dates for testing."""
    today = datetime.now()
    return [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]


@pytest.fixture
def sample_price_data(sample_dates):
    """Sample stock price data for testing."""
    base_price = 180.0
    prices = []
    volumes = []
    
    for i in range(30):
        change = (i % 5 - 2) * 0.5  # Create some cyclical patterns
        random_factor = (i % 7) * 0.3  # Add some randomness
        price = base_price + change + random_factor
        volume = int(5000000 + (i % 5) * 1000000)
        
        prices.append(price)
        volumes.append(volume)
    
    return {
        "dates": sample_dates,
        "prices": prices,
        "volumes": volumes
    }


@pytest.fixture
def sample_technical_indicators(sample_price_data):
    """Sample technical indicators for testing."""
    prices = sample_price_data["prices"]
    return {
        "rsi": [45 + (i % 10) for i in range(30)],
        "macd": [0.5 + (i % 5) * 0.1 for i in range(30)],
        "macd_signal": [0.4 + (i % 5) * 0.1 for i in range(30)],
        "moving_averages": {
            "MA50": [p * 0.98 for p in prices],
            "MA200": [p * 0.95 for p in prices]
        }
    }


@pytest.fixture
def sample_fundamental_metrics():
    """Sample fundamental metrics for testing."""
    return {
        "pe_ratio": {"value": 28.5, "industry_avg": 25.0},
        "roe": {"value": 0.35, "industry_avg": 0.28},
        "profit_margin": {"value": 0.22, "industry_avg": 0.18},
        "debt_to_equity": {"value": 1.2, "industry_avg": 1.5},
        "current_ratio": {"value": 1.8, "industry_avg": 1.5}
    }


@pytest.fixture
def sample_sentiment_data(sample_dates):
    """Sample sentiment data for testing."""
    return {
        "overall_score": 0.65,
        "summary": "Recent iPhone sales data and positive analyst coverage contribute to bullish sentiment",
        "news_items": [
            {
                "title": "Apple Reports Strong Q3 Results",
                "source": "Financial Times",
                "date": sample_dates[5],
                "sentiment": 0.8,
                "url": "https://example.com/news1"
            },
            {
                "title": "New iPhone Pro Max Sets Sales Record",
                "source": "Tech Today",
                "date": sample_dates[3],
                "sentiment": 0.9,
                "url": "https://example.com/news2"
            },
            {
                "title": "Apple Faces Supply Chain Challenges",
                "source": "Wall Street Journal",
                "date": sample_dates[7],
                "sentiment": -0.2,
                "url": "https://example.com/news3"
            }
        ],
        "integrated_score": 72
    }


@pytest.fixture
def sample_ui_component_config():
    """Sample UI component configuration."""
    return {
        "cards": [
            {
                "title": "Price",
                "content": {
                    "value": "$185.92", 
                    "description": "Current price",
                    "trend": "+1.2%",
                    "trendDirection": "up"
                }
            },
            {
                "title": "Technical Health",
                "content": {
                    "value": "Strong",
                    "description": "Technical indicators look positive"
                }
            }
        ],
        "charts": [
            {
                "type": "line",
                "data": {
                    "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
                    "datasets": [{
                        "label": "Stock Price",
                        "data": [150, 155, 160, 158, 162]
                    }]
                }
            }
        ]
    }
