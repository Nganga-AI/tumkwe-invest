"""
Collector for company news articles.
"""

import time
from datetime import datetime, timedelta
from typing import List

import requests

from ..config import NEWS_API_KEY
from ..models import NewsArticle


def get_company_news(
    company_symbol: str = None,
    company_name: str = None,
    days: int = 5,
    max_articles: int = 25,
) -> List[NewsArticle]:
    """
    Get news articles about a specific company.

    Args:
        company_symbol: Stock ticker symbol
        company_name: Company name for search
        days: Number of days to look back
        max_articles: Maximum number of articles to retrieve

    Returns:
        List of NewsArticle objects
    """
    if not NEWS_API_KEY:
        print("Warning: NEWS_API_KEY not set. Cannot fetch news.")
        return []

    if not company_symbol and not company_name:
        raise ValueError("Must provide company_symbol or company_name")

    articles = []
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": str(company_name or company_symbol),
            "language": "en",
            # "sortBy": "publishedAt",
            "sortBy": "popularity",
            "pageSize": max_articles,
            "apiKey": NEWS_API_KEY,
            "from": (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
            "to": datetime.now().strftime("%Y-%m-%d"),
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        for article in data.get("articles", []):
            try:
                pub_date = datetime.strptime(
                    article.get("publishedAt"), "%Y-%m-%dT%H:%M:%SZ"
                )
                news = NewsArticle(
                    company_symbol=company_symbol,
                    title=article.get("title", ""),
                    publication=article.get("source", {}).get("name", "Unknown"),
                    date=pub_date,
                    url=article.get("url", ""),
                    summary=article.get("description", ""),
                )

                articles.append(news)
            except Exception as e:
                print(f"Error processing article: {e}")

            # Be kind to servers by adding a small delay
            time.sleep(0.5)

    except Exception as e:
        print(f"Error fetching news for {company_name}: {e}")

    return articles
