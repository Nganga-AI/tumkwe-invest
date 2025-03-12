"""
Collector for company news articles.
"""
import requests
from datetime import datetime
from typing import List, Optional
from newspaper import Article
import time

from ..models import NewsArticle
from ..config import NEWS_API_KEY


def get_company_news(company_symbol: str, company_name: str, days: int = 30) -> List[NewsArticle]:
    """
    Get news articles about a specific company.
    
    Args:
        company_symbol: Stock ticker symbol
        company_name: Company name for search
        days: Number of days to look back
        
    Returns:
        List of NewsArticle objects
    """
    if not NEWS_API_KEY:
        print("Warning: NEWS_API_KEY not set. Cannot fetch news.")
        return []
    
    articles = []
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": f"{company_name} OR {company_symbol}",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 25,
            "apiKey": NEWS_API_KEY,
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        for article in data.get("articles", []):
            try:
                pub_date = datetime.strptime(article.get("publishedAt"), "%Y-%m-%dT%H:%M:%SZ")
                news = NewsArticle(
                    company_symbol=company_symbol,
                    title=article.get("title", ""),
                    publication=article.get("source", {}).get("name", "Unknown"),
                    date=pub_date,
                    url=article.get("url", ""),
                    summary=article.get("description", "")
                )
                
                # Try to fetch full content (may not always work due to site restrictions)
                try:
                    full_article = Article(article.get("url"))
                    full_article.download()
                    full_article.parse()
                    news.content = full_article.text
                except Exception as e:
                    pass
                    
                articles.append(news)
            except Exception as e:
                print(f"Error processing article: {e}")
            
            # Be kind to servers by adding a small delay
            time.sleep(0.5)
            
    except Exception as e:
        print(f"Error fetching news for {company_name}: {e}")
    
    return articles
