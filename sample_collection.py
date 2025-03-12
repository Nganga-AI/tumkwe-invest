"""
Sample script to demonstrate data collection functionality.
"""
import os
import json
from datetime import datetime
import pandas as pd
from tqdm import tqdm

from datacollection.collectors.yahoo_finance import (
    get_stock_data,
    get_company_profile,
    get_financial_statements
)
from datacollection.collectors.news_collector import get_company_news
from datacollection.config import DEFAULT_START_DATE, DEFAULT_END_DATE


def sample_data_collection(symbol="AAPL", start_date=DEFAULT_START_DATE, end_date=DEFAULT_END_DATE):
    """
    Demonstrate data collection for a sample company.
    
    Args:
        symbol: The stock symbol to analyze
        start_date: Start date for historical data
        end_date: End date for historical data
    """
    print(f"\n{'='*50}")
    print(f"Collecting data for {symbol}")
    print(f"{'='*50}")
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(__file__), "collected_data")
    company_dir = os.path.join(data_dir, symbol)
    os.makedirs(company_dir, exist_ok=True)
    
    # 1. Get company profile
    print("\nFetching company profile...")
    profile = get_company_profile(symbol)
    if profile:
        print(f"Company: {profile.name}")
        print(f"Sector: {profile.sector}")
        print(f"Industry: {profile.industry}")
        print(f"Employees: {profile.employees}")
        
        # Save profile to file
        with open(os.path.join(company_dir, "profile.json"), "w") as f:
            # Convert dataclass to dict, handling datetime objects
            profile_dict = {
                key: value if not isinstance(value, datetime) else value.isoformat() 
                for key, value in profile.__dict__.items()
            }
            json.dump(profile_dict, f, indent=4)
    else:
        print("Failed to fetch company profile")
    
    # 2. Get stock price data
    print("\nFetching historical stock prices...")
    stock_prices = get_stock_data(symbol, start_date, end_date)
    if stock_prices:
        print(f"Collected {len(stock_prices)} days of stock price data")
        
        # Convert to pandas DataFrame and save to CSV
        price_data = pd.DataFrame([
            {
                'date': price.date.date().isoformat(),
                'open': price.open,
                'high': price.high,
                'low': price.low,
                'close': price.close,
                'volume': price.volume,
                'adjusted_close': price.adjusted_close
            }
            for price in stock_prices
        ])
        price_data.to_csv(os.path.join(company_dir, "stock_prices.csv"), index=False)
    else:
        print("No stock price data collected")
    
    # 3. Get financial statements
    print("\nFetching financial statements...")
    financial_statements = get_financial_statements(symbol)
    
    for statement_type, statements in financial_statements.items():
        if statements:
            print(f"Collected {len(statements)} {statement_type} statements")
            
            # Save each statement type to a separate file
            with open(os.path.join(company_dir, f"{statement_type}.json"), "w") as f:
                # Convert dataclasses to dicts, handling datetime objects
                statements_dicts = [
                    {
                        key: value if not isinstance(value, datetime) else value.isoformat()
                        for key, value in statement.__dict__.items()
                    }
                    for statement in statements
                ]
                json.dump(statements_dicts, f, indent=4)
        else:
            print(f"No {statement_type} data collected")
    
    # 4. Get news articles if the profile was successfully fetched
    if profile:
        print("\nFetching news articles...")
        news = get_company_news(symbol, profile.name, days=30)
        if news:
            print(f"Collected {len(news)} news articles")
            
            # Save news to CSV
            news_data = pd.DataFrame([
                {
                    'title': article.title,
                    'publication': article.publication,
                    'date': article.date.isoformat() if article.date else None,
                    'url': article.url,
                    'summary': article.summary[:100] + '...' if article.summary and len(article.summary) > 100 else article.summary
                }
                for article in news
            ])
            news_data.to_csv(os.path.join(company_dir, "news_articles.csv"), index=False)
            
            # Save full article content separately
            for i, article in enumerate(news):
                if article.content:
                    with open(os.path.join(company_dir, f"article_{i}.txt"), "w") as f:
                        f.write(f"Title: {article.title}\n")
                        f.write(f"Source: {article.publication}\n")
                        f.write(f"Date: {article.date.isoformat() if article.date else 'Unknown'}\n")
                        f.write(f"URL: {article.url}\n\n")
                        f.write(article.content)
        else:
            print("No news articles collected")
    
    print(f"\n{'='*50}")
    print(f"Data collection complete for {symbol}")
    print(f"Data saved to: {company_dir}")
    print(f"{'='*50}")


if __name__ == "__main__":
    # Example usage
    sample_symbols = ["AAPL", "MSFT", "GOOGL"]
    
    for symbol in tqdm(sample_symbols, desc="Processing companies"):
        sample_data_collection(symbol)
