"""
Collector for company news articles from Yahoo Finance.
"""
import yfinance as yf
from datetime import datetime
from typing import List, Optional
import time

from ..models import NewsArticle


def get_yahoo_finance_news(company_symbol: str, max_articles: int = 25) -> List[NewsArticle]:
    """
    Get news articles about a specific company from Yahoo Finance.
    
    Args:
        company_symbol: Stock ticker symbol
        max_articles: Maximum number of articles to retrieve
        
    Returns:
        List of NewsArticle objects
    """
    articles = []
    try:
        # Create a ticker object
        ticker = yf.Ticker(company_symbol)
        
        # Get news data
        news_data = ticker.news
        
        # Process each news article (up to max_articles)
        for article_data in news_data[:max_articles]:
            try:
                # Convert timestamp to datetime
                pub_date = datetime.fromtimestamp(article_data.get('providerPublishTime', 0))
                
                # Create NewsArticle object
                news = NewsArticle(
                    company_symbol=company_symbol,
                    title=article_data.get('title', ''),
                    publication=article_data.get('publisher', 'Yahoo Finance'),
                    date=pub_date,
                    url=article_data.get('link', ''),
                    summary=article_data.get('summary', '')
                )
                
                articles.append(news)
            except Exception as e:
                print(f"Error processing Yahoo Finance article: {e}")
            
        print(f"Successfully retrieved {len(articles)} news articles for {company_symbol} from Yahoo Finance")
            
    except Exception as e:
        print(f"Error fetching Yahoo Finance news for {company_symbol}: {e}")
    
    return articles
