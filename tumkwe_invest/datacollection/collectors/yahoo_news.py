"""
Collector for company news articles from Yahoo Finance.
"""

from datetime import datetime
from typing import List, Union

import yfinance as yf

from ..models import NewsArticle


def get_yahoo_finance_news(
    company_symbol: str, max_articles: int = 25
) -> List[NewsArticle]:
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
                article_data: dict[str, Union[str, dict, bool]] = article_data[
                    "content"
                ]
                # Convert timestamp to datetime
                pub_date = datetime.strptime(
                    article_data.get(
                        "pubDate", datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                    ),
                    "%Y-%m-%dT%H:%M:%SZ",
                )

                # Create NewsArticle object
                news = NewsArticle(
                    company_symbol=company_symbol,
                    title=article_data.get("title", ""),
                    publication=article_data.get("provider", {}).get(
                        "displayName", "Yahoo Finance"
                    ),
                    date=pub_date,
                    url=article_data.get("clickThroughUrl", {}).get("url", ""),
                    summary=article_data.get("summary", ""),
                )

                articles.append(news)
            except Exception as e:
                print(f"Error processing Yahoo Finance article: {e}")

        print(
            f"Successfully retrieved {len(articles)} news articles for {company_symbol} from Yahoo Finance"
        )

    except Exception as e:
        print(f"Error fetching Yahoo Finance news for {company_symbol}: {e}")

    return articles
