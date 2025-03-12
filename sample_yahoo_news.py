"""
Sample script to demonstrate Yahoo Finance news collection functionality.
"""
import os
import pandas as pd
from tqdm import tqdm

from datacollection.collectors.yahoo_news import get_yahoo_finance_news
from datacollection.collectors.yahoo_finance import get_company_profile


def sample_yahoo_news_collection(symbols=None):
    """
    Demonstrate Yahoo Finance news collection for sample companies.
    
    Args:
        symbols: List of stock symbols to analyze, defaults to ['AAPL', 'MSFT', 'GOOGL']
    """
    if symbols is None:
        symbols = ["AAPL", "MSFT", "GOOGL"]
    
    print(f"\n{'='*50}")
    print(f"Collecting Yahoo Finance news")
    print(f"{'='*50}")
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(__file__), "collected_data")
    os.makedirs(data_dir, exist_ok=True)
    
    all_news = []
    
    for symbol in tqdm(symbols, desc="Processing companies"):
        print(f"\nCollecting news for {symbol}...")
        
        # Create company directory
        company_dir = os.path.join(data_dir, symbol)
        os.makedirs(company_dir, exist_ok=True)
        
        # Get company profile to have the company name
        profile = get_company_profile(symbol)
        company_name = profile.name if profile else symbol
        
        # Get news from Yahoo Finance
        news_articles = get_yahoo_finance_news(symbol)
        
        if news_articles:
            print(f"Collected {len(news_articles)} news articles for {company_name}")
            
            # Save news to CSV
            news_data = pd.DataFrame([
                {
                    'symbol': symbol,
                    'company': company_name,
                    'title': article.title,
                    'publication': article.publication,
                    'date': article.date.isoformat() if article.date else None,
                    'url': article.url,
                    'summary': article.summary[:100] + '...' if article.summary and len(article.summary) > 100 else article.summary
                }
                for article in news_articles
            ])
            
            # Save to company-specific CSV
            news_data.to_csv(os.path.join(company_dir, "yahoo_news.csv"), index=False)
            
            # Add to combined dataset
            all_news.append(news_data)
        else:
            print(f"No news articles collected for {company_name}")
    
    # Combine all news articles into one dataset
    if all_news:
        combined_news = pd.concat(all_news, ignore_index=True)
        combined_news.to_csv(os.path.join(data_dir, "all_yahoo_news.csv"), index=False)
        print(f"\nSaved {len(combined_news)} total news articles to {os.path.join(data_dir, 'all_yahoo_news.csv')}")
    
    print(f"\n{'='*50}")
    print(f"Yahoo Finance news collection complete")
    print(f"{'='*50}")


if __name__ == "__main__":
    # Example usage with default symbols
    sample_yahoo_news_collection()
    
    # Example with custom symbols
    # sample_yahoo_news_collection(["TSLA", "AMZN", "META"])
