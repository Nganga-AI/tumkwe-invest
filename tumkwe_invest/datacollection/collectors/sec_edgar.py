"""
Collector for SEC EDGAR filings.

=> @TODO Not working : to_delete
"""

import json
import os
import re
import time
from datetime import datetime
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from ..config import API_RATE_LIMITS, CACHE_DIRECTORY, SEC_USER_AGENT
from ..models import SECFiling
from loguru import logger
# Create cache directory
os.makedirs(os.path.join(CACHE_DIRECTORY, "sec_filings"), exist_ok=True)

# Rate limiting setup
SEC_RATE_LIMIT = API_RATE_LIMITS["sec_edgar"]["requests_per_second"]
last_request_time = 0


def _respect_rate_limit():
    """Ensure we respect SEC's rate limit"""
    global last_request_time
    current_time = time.time()
    sleep_time = max(0, (1 / SEC_RATE_LIMIT) - (current_time - last_request_time))

    if sleep_time > 0:
        time.sleep(sleep_time)

    last_request_time = time.time()


def get_cik_by_ticker(ticker: str) -> Optional[str]:
    """
    Get the CIK number for a company ticker.

    Args:
        ticker: The stock ticker symbol

    Returns:
        CIK number as string or None if not found
    """
    cache_file = os.path.join(CACHE_DIRECTORY, "sec_filings", f"{ticker}_cik.json")

    # Try to get from cache first
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            cached_data = json.load(f)
            if "cik" in cached_data:
                return cached_data["cik"]

    try:
        _respect_rate_limit()
        url = "https://www.sec.gov/cgi-bin/browse-edgar"
        params = {"CIK": ticker, "owner": "exclude", "action": "getcompany"}
        headers = {"User-Agent": SEC_USER_AGENT}

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        # Extract CIK from the response
        soup = BeautifulSoup(response.text, "html.parser")
        cik_text = soup.find(string=re.compile(r"CIK.*\d{10}"))

        if cik_text:
            cik = re.search(r"\d{10}", cik_text).group(0)

            # Cache the result
            with open(cache_file, "w") as f:
                json.dump({"ticker": ticker, "cik": cik}, f)

            return cik
        else:
            logger.info(f"Could not find CIK for {ticker}")
            return None

    except Exception as e:
        logger.error(f"Error getting CIK for {ticker}: {e}")
        return None


def get_recent_filings(
    ticker: str, filing_types: List[str] = None, count: int = 10
) -> List[SECFiling]:
    """
    Get recent SEC filings for a company.

    Args:
        ticker: The stock ticker symbol
        filing_types: List of filing types to retrieve (e.g., ["10-K", "10-Q"])
        count: Maximum number of filings to retrieve

    Returns:
        List of SECFiling objects
    """
    if filing_types is None:
        filing_types = ["10-K", "10-Q", "8-K"]

    filings = []
    cik = get_cik_by_ticker(ticker)

    if not cik:
        return filings

    try:
        _respect_rate_limit()
        url = "https://www.sec.gov/cgi-bin/browse-edgar"
        params = {
            "action": "getcompany",
            "CIK": cik,
            "type": ",".join(filing_types),
            "owner": "exclude",
            "count": count,
        }
        headers = {"User-Agent": SEC_USER_AGENT}

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        # Parse the response to extract filing information
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("tr")

        for row in results:
            cols = row.find_all("td")
            if len(cols) >= 4:
                try:
                    filing_type = cols[0].text.strip()

                    if filing_type in filing_types:
                        filing_date_str = cols[3].text.strip()
                        filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d")

                        # Get the document URL
                        doc_link = cols[1].find("a")
                        if doc_link and "href" in doc_link.attrs:
                            doc_href = doc_link["href"]
                            doc_url = f"https://www.sec.gov{doc_href}"

                            # Extract accession number
                            accession_match = re.search(
                                r"/(\d{10}-\d{2}-\d+)/", doc_url
                            )
                            accession_number = (
                                accession_match.group(1) if accession_match else None
                            )

                            filing = SECFiling(
                                company_symbol=ticker,
                                filing_type=filing_type,
                                filing_date=filing_date,
                                accession_number=accession_number,
                                url=doc_url,
                            )

                            filings.append(filing)
                except Exception as e:
                    logger.error(f"Error processing filing row: {e}")

    except Exception as e:
        logger.error(f"Error fetching SEC filings for {ticker}: {e}")

    return filings


def download_filing_document(filing: SECFiling) -> Optional[str]:
    """
    Download and return the text of an SEC filing.

    Args:
        filing: SECFiling object with URL

    Returns:
        Text content of the filing or None
    """
    if not filing.url:
        return None

    cache_file = os.path.join(
        CACHE_DIRECTORY,
        "sec_filings",
        f"{filing.company_symbol}_{filing.filing_type}_{filing.accession_number}.txt",
    )

    # Try to get from cache first
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    try:
        _respect_rate_limit()
        headers = {"User-Agent": SEC_USER_AGENT}

        # Find the actual document URL
        index_response = requests.get(filing.url, headers=headers)
        index_response.raise_for_status()

        index_soup = BeautifulSoup(index_response.text, "html.parser")
        table = index_soup.find("table", summary="Document Format Files")

        if table:
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 3:
                    # Look for the main document (usually has "htm" or "html" in description)
                    desc = cells[1].text.lower()
                    if ".htm" in desc and filing.filing_type.lower() in desc:
                        doc_link = cells[2].find("a")
                        if doc_link and "href" in doc_link.attrs:
                            doc_path = doc_link["href"]
                            doc_url = f"https://www.sec.gov{doc_path}"

                            # Download the actual document
                            _respect_rate_limit()
                            doc_response = requests.get(doc_url, headers=headers)
                            doc_response.raise_for_status()

                            doc_soup = BeautifulSoup(doc_response.text, "html.parser")

                            # Extract text content
                            content = doc_soup.get_text(" ", strip=True)

                            # Cache the content
                            with open(cache_file, "w", encoding="utf-8") as f:
                                f.write(content)

                            return content

        logger.info(
            f"Could not find document content for {filing.company_symbol} {filing.filing_type}"
        )
        return None

    except Exception as e:
        logger.error(f"Error downloading filing document: {e}")
        return None
