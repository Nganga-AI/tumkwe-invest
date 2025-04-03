from datetime import datetime

import yfinance as yf
from langchain_core.tools import tool
from loguru import logger


@tool(parse_docstring=True)
def fetch_company_news(
    ticker: str,
    max_articles: int = 10,
) -> list:
    """
    Fetch recent news articles about a specific company or stock.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT) or company name. \
            Works most reliably with standard ticker symbols.
        max_articles: Maximum number of news articles to retrieve. \
            Default is 10. Higher values may result in more comprehensive but slower results.

    Returns:
        List of news articles, where each article is a dictionary containing title, \
        summary, publication date, and source information. If no direct results are found, \
        falls back to search with simplified article information.
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
            "providerPublishTime": (
                datetime.fromtimestamp(article.get("providerPublishTime")).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if article.get("providerPublishTime")
                else None
            ),
        }
        for article in results
    ]
    return results


tools = [
    fetch_company_news,
]
TOOL_DESCRIPTION = """
Handles queries about current events, news articles, and searching news archives.
It fetches the latest company news and articles using yfinance.
"""
