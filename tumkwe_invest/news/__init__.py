from langchain_core.tools import tool
import yfinance as yf
from datetime import datetime
from  loguru import logger

@tool
def fetch_company_news(
    ticker: str,
    max_articles: int = 10,
) -> list:
    """
    Fetch news articles about a specific company.

    Args:
        ticker: Stock ticker symbol or company name for search
        max_articles: Maximum number of articles to retrieve

    Returns:
        List news
    """
    results: list = yf.Ticker(ticker).get_news(count=max_articles)
    if results:
        results = [
            {
                "title": article["content"]["title"],
                "summary": article["content"]["summary"],
                "pubDate": article["content"].get("pubDate"),
                "source": article["content"].get("provider"),
            }
            for article in results
        ]
        return results
    logger.warning(f"No results found for {ticker}.")
    # Fallback to search if no results found
    results = yf.Search(ticker, enable_fuzzy_query=True, news_count=max_articles).news
    results = [
        {
            "title": article["title"],
            "source": article.get("publisher"),
            "providerPublishTime": datetime.fromtimestamp(
                article.get("providerPublishTime")
            ).strftime("%Y-%m-%d %H:%M:%S") if article.get("providerPublishTime") else None,
        }
        for article in results
    ]
    return results
