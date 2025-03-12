"""
Configuration settings for data collection.
Store API keys and other settings.
"""
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# API Keys (stored in .env file for security)
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "TumkweInvest myname@example.com")  # SEC filings require user agent

# Data collection settings
DEFAULT_START_DATE = "2020-01-01"
DEFAULT_END_DATE = datetime.now().strftime("%Y-%m-%d")
DATA_REFRESH_INTERVAL = {
    "market_data": timedelta(hours=4),  # Update market data every 4 hours during market hours
    "financial_statements": timedelta(days=7),  # Update financial statements weekly
    "news": timedelta(hours=6),  # Update news every 6 hours
    "sec_filings": timedelta(days=1)  # Update SEC filings daily
}

# Cache settings
CACHE_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data_cache")
CACHE_EXPIRY = {
    "market_data": timedelta(days=1),
    "financial_statements": timedelta(days=30),
    "news": timedelta(days=1),
    "sec_filings": timedelta(days=7)
}

# Request limits to stay within free tier
API_RATE_LIMITS = {
    "alpha_vantage": {"requests_per_minute": 5, "requests_per_day": 500},
    "yahoo_finance": {"requests_per_minute": 2000, "requests_per_hour": 48000},  # Unofficial limits
    "news_api": {"requests_per_day": 100},
    "sec_edgar": {"requests_per_second": 10}  # SEC EDGAR fair use policy
}

# Supported data providers
PROVIDERS = {
    "yahoo": "Yahoo Finance (free)",
    "alpha_vantage": "Alpha Vantage (requires API key)",
    "news": "News API (requires API key)",
    "yahoo_news": "Yahoo Finance News (free)",
    "sec_edgar": "SEC EDGAR Filings (free)",
    "finnhub": "Finnhub (requires API key)"
}

# Data validation thresholds
VALIDATION = {
    "max_price_change_percent": 25,  # Flag price changes > 25% in a single day
    "min_data_completeness": 0.95,   # Require at least 95% of expected data points
    "max_pe_ratio": 500,             # Flag unusually high P/E ratios
    "max_outlier_std": 3             # Flag values > 3 standard deviations from mean
}
