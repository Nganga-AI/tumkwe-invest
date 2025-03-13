"""
Manager for coordinating data collection tasks and scheduling.
"""

import json
import logging
import os
import pickle
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

import pandas as pd

from .collectors.financial_metrics import (
    get_comprehensive_metrics,
    get_quarterly_financial_data,
)
from .collectors.news_collector import get_company_news
from .collectors.sec_edgar import download_filing_document, get_recent_filings
from .collectors.yahoo_finance import (
    get_company_profile,
    get_financial_statements,
    get_stock_data,
)
from .collectors.yahoo_news import get_yahoo_finance_news
from .config import CACHE_DIRECTORY, DATA_REFRESH_INTERVAL
from .models import DataCollectionTask, ValidationReport
from .validation import (
    generate_combined_report,
    validate_company_profile,
    validate_financial_statement,
    validate_key_metrics,
    validate_news_articles,
    validate_stock_prices,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(CACHE_DIRECTORY, "data_collection.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("data_collector")


class CollectorManager:
    """Manager for data collection tasks."""

    def __init__(self, output_dir: str = None):
        """
        Initialize the collector manager.

        Args:
            output_dir: Directory to store collected data (defaults to CACHE_DIRECTORY)
        """
        self.output_dir = output_dir or CACHE_DIRECTORY
        self.tasks: List[DataCollectionTask] = []
        self.running = False
        self.thread = None
        self.symbols_monitored: Set[str] = set()
        self.last_validation: Dict[str, ValidationReport] = {}

        # Create necessary directories
        os.makedirs(self.output_dir, exist_ok=True)

        # Task state file
        self.tasks_file = os.path.join(self.output_dir, "collection_tasks.pickle")

        # Load existing tasks if available
        self._load_tasks()

    def _load_tasks(self):
        """Load tasks from saved state."""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, "rb") as f:
                    self.tasks = pickle.load(f)
                logger.info(f"Loaded {len(self.tasks)} tasks from saved state")

                # Update symbols monitored
                for task in self.tasks:
                    self.symbols_monitored.update(task.company_symbols)

            except Exception as e:
                logger.error(f"Failed to load tasks: {e}")
                self.tasks = []
        else:
            logger.info("No saved tasks found")

    def _save_tasks(self):
        """Save tasks to disk."""
        try:
            with open(self.tasks_file, "wb") as f:
                pickle.dump(self.tasks, f)
            logger.info(f"Saved {len(self.tasks)} tasks to disk")
        except Exception as e:
            logger.error(f"Failed to save tasks: {e}")

    def add_company(self, symbol: str, name: Optional[str] = None):
        """
        Add a company to monitor.

        Args:
            symbol: Stock ticker symbol
            name: Company name (fetched if not provided)
        """
        if symbol in self.symbols_monitored:
            logger.info(f"Company {symbol} already monitored")
            return

        # Get company name if not provided
        if not name:
            try:
                profile = get_company_profile(symbol)
                if profile:
                    name = profile.name
                else:
                    name = symbol
            except Exception as e:
                logger.error(f"Failed to get company profile for {symbol}: {e}")
                name = symbol

        # Add tasks for this company
        self._add_market_data_task(symbol)
        self._add_financials_task(symbol)
        self._add_news_task(symbol)
        self._add_sec_filings_task(symbol)

        # Update monitored symbols
        self.symbols_monitored.add(symbol)
        logger.info(f"Added company {name} ({symbol}) for monitoring")

    def remove_company(self, symbol: str):
        """
        Remove a company from monitoring.

        Args:
            symbol: Stock ticker symbol
        """
        if symbol not in self.symbols_monitored:
            logger.info(f"Company {symbol} not being monitored")
            return

        # Remove tasks for this company
        self.tasks = [task for task in self.tasks if symbol not in task.company_symbols]

        # Remove from monitored symbols
        self.symbols_monitored.remove(symbol)
        logger.info(f"Removed company {symbol} from monitoring")

        # Save updated task list
        self._save_tasks()

    def _add_market_data_task(self, symbol: str):
        """Add market data collection task for a company."""
        task = DataCollectionTask(
            task_name=f"market_data_{symbol}",
            data_type="market_data",
            company_symbols=[symbol],
            next_run=datetime.now(),
            interval=DATA_REFRESH_INTERVAL["market_data"],
        )
        self.tasks.append(task)
        self._save_tasks()

    def _add_financials_task(self, symbol: str):
        """Add financial data collection task for a company."""
        task = DataCollectionTask(
            task_name=f"financial_data_{symbol}",
            data_type="financial_statements",
            company_symbols=[symbol],
            next_run=datetime.now(),
            interval=DATA_REFRESH_INTERVAL["financial_statements"],
        )
        self.tasks.append(task)
        self._save_tasks()

    def _add_news_task(self, symbol: str):
        """Add news collection task for a company."""
        task = DataCollectionTask(
            task_name=f"news_{symbol}",
            data_type="news",
            company_symbols=[symbol],
            next_run=datetime.now(),
            interval=DATA_REFRESH_INTERVAL["news"],
        )
        self.tasks.append(task)
        self._save_tasks()

    def _add_sec_filings_task(self, symbol: str):
        """Add SEC filings collection task for a company."""
        task = DataCollectionTask(
            task_name=f"sec_filings_{symbol}",
            data_type="sec_filings",
            company_symbols=[symbol],
            next_run=datetime.now(),
            interval=DATA_REFRESH_INTERVAL["sec_filings"],
        )
        self.tasks.append(task)
        self._save_tasks()

    def get_due_tasks(self) -> List[DataCollectionTask]:
        """Get collection tasks that are due to run."""
        now = datetime.now()
        return [task for task in self.tasks if task.next_run <= now]

    def start_collection_thread(self):
        """Start the collection thread."""
        if self.running:
            logger.info("Collection thread already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._collection_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Started collection thread")

    def stop_collection_thread(self):
        """Stop the collection thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)
            logger.info("Stopped collection thread")

    def _collection_loop(self):
        """Main collection loop."""
        while self.running:
            due_tasks = self.get_due_tasks()

            if due_tasks:
                logger.info(f"Processing {len(due_tasks)} due tasks")

                for task in due_tasks:
                    try:
                        self._execute_task(task)

                        # Update task timing
                        task.last_run = datetime.now()
                        task.next_run = task.last_run + task.interval
                    except Exception as e:
                        logger.error(f"Error executing task {task.task_name}: {e}")

                # Save updated task state
                self._save_tasks()

            # Sleep before checking again
            time.sleep(60)  # Check every minute

    def _execute_task(self, task: DataCollectionTask):
        """
        Execute a collection task.

        Args:
            task: The task to execute
        """
        logger.info(f"Executing task {task.task_name}")

        if task.data_type == "market_data":
            self._collect_market_data(task)
        elif task.data_type == "financial_statements":
            self._collect_financial_data(task)
        elif task.data_type == "news":
            self._collect_news(task)
        elif task.data_type == "sec_filings":
            self._collect_sec_filings(task)

    def _collect_market_data(self, task: DataCollectionTask):
        """Collect market data for the given task."""
        for symbol in task.company_symbols:
            try:
                company_dir = self._get_company_dir(symbol)

                # Get last 30 days of market data (or update from last save)
                end_date = datetime.now().strftime("%Y-%m-%d")

                # Check if we have existing data to just update
                prices_file = os.path.join(company_dir, "stock_prices.csv")
                if os.path.exists(prices_file):
                    existing_prices = pd.read_csv(prices_file)
                    if not existing_prices.empty:
                        # Get latest date and add one day
                        latest_date = pd.to_datetime(existing_prices["date"]).max()
                        start_date = (latest_date + timedelta(days=1)).strftime(
                            "%Y-%m-%d"
                        )
                    else:
                        start_date = (
                            datetime.now() - timedelta(days=365 * 2)
                        ).strftime("%Y-%m-%d")
                else:
                    # Get 2 years of historical data
                    start_date = (datetime.now() - timedelta(days=365 * 2)).strftime(
                        "%Y-%m-%d"
                    )

                # Get stock data
                prices = get_stock_data(symbol, start_date, end_date)

                if prices:
                    # Validate the data
                    validation_report = validate_stock_prices(prices, symbol)
                    self.last_validation[f"market_data_{symbol}"] = validation_report

                    # Convert to dataframe
                    new_prices_df = pd.DataFrame(
                        [
                            {
                                "date": price.date.date().isoformat(),
                                "open": price.open,
                                "high": price.high,
                                "low": price.low,
                                "close": price.close,
                                "volume": price.volume,
                                "adjusted_close": price.adjusted_close,
                                "is_valid": price.is_valid,
                            }
                            for price in prices
                        ]
                    )

                    # Merge with existing data if it exists
                    if os.path.exists(prices_file):
                        existing_prices = pd.read_csv(prices_file)
                        combined_prices = pd.concat([existing_prices, new_prices_df])
                        combined_prices = combined_prices.drop_duplicates(
                            subset=["date"]
                        )
                        combined_prices.to_csv(prices_file, index=False)
                    else:
                        new_prices_df.to_csv(prices_file, index=False)

                    # Get additional metrics
                    metrics = get_comprehensive_metrics(symbol)
                    if metrics:
                        metrics_validation = validate_key_metrics(metrics)
                        self.last_validation[f"metrics_{symbol}"] = metrics_validation

                        # Save metrics data
                        metrics_file = os.path.join(company_dir, "key_metrics.json")
                        with open(metrics_file, "w") as f:
                            # Convert to dict
                            metrics_dict = {
                                k: v
                                for k, v in metrics.__dict__.items()
                                if not k.startswith("_") and k != "validation_warnings"
                            }
                            # Handle datetime
                            metrics_dict["date"] = metrics_dict["date"].isoformat()
                            metrics_dict["last_updated"] = metrics_dict[
                                "last_updated"
                            ].isoformat()
                            json.dump(metrics_dict, f, indent=4)

                logger.info(f"Market data collection complete for {symbol}")

            except Exception as e:
                logger.error(f"Error collecting market data for {symbol}: {e}")

    def _collect_financial_data(self, task: DataCollectionTask):
        """Collect financial data for the given task."""
        for symbol in task.company_symbols:
            try:
                company_dir = self._get_company_dir(symbol)

                # Get company profile
                profile = get_company_profile(symbol)
                if profile:
                    validation_report = validate_company_profile(profile)
                    self.last_validation[f"profile_{symbol}"] = validation_report

                    # Save profile data
                    profile_file = os.path.join(company_dir, "profile.json")
                    with open(profile_file, "w") as f:
                        profile_dict = {
                            k: v
                            for k, v in profile.__dict__.items()
                            if not k.startswith("_") and k != "validation_warnings"
                        }
                        # Handle datetime
                        profile_dict["last_updated"] = profile_dict[
                            "last_updated"
                        ].isoformat()
                        if "ipo_date" in profile_dict and profile_dict["ipo_date"]:
                            profile_dict["ipo_date"] = profile_dict[
                                "ipo_date"
                            ].isoformat()
                        json.dump(profile_dict, f, indent=4)

                # Get financial statements
                statements = get_financial_statements(symbol)

                for statement_type, statement_list in statements.items():
                    if statement_list:
                        # Validate each statement
                        for statement in statement_list:
                            validation_report = validate_financial_statement(statement)
                            key = f"{statement_type}_{symbol}_{statement.date.strftime('%Y%m%d')}"
                            self.last_validation[key] = validation_report

                        # Save statement data
                        statement_file = os.path.join(
                            company_dir, f"{statement_type}.json"
                        )
                        with open(statement_file, "w") as f:
                            statements_dict = []
                            for statement in statement_list:
                                stmt_dict = {
                                    k: v
                                    for k, v in statement.__dict__.items()
                                    if not k.startswith("_")
                                    and k != "validation_warnings"
                                }
                                # Handle datetime
                                stmt_dict["date"] = stmt_dict["date"].isoformat()
                                stmt_dict["last_updated"] = stmt_dict[
                                    "last_updated"
                                ].isoformat()
                                statements_dict.append(stmt_dict)
                            json.dump(statements_dict, f, indent=4)

                # Get quarterly financial data
                qtr_statements = get_quarterly_financial_data(symbol)

                for statement_type, statement_list in qtr_statements.items():
                    if statement_list:
                        # Save quarterly statement data
                        statement_file = os.path.join(
                            company_dir, f"quarterly_{statement_type}.json"
                        )
                        with open(statement_file, "w") as f:
                            statements_dict = []
                            for statement in statement_list:
                                stmt_dict = {
                                    k: v
                                    for k, v in statement.__dict__.items()
                                    if not k.startswith("_")
                                    and k != "validation_warnings"
                                }
                                # Handle datetime
                                stmt_dict["date"] = stmt_dict["date"].isoformat()
                                stmt_dict["last_updated"] = stmt_dict[
                                    "last_updated"
                                ].isoformat()
                                statements_dict.append(stmt_dict)
                            json.dump(statements_dict, f, indent=4)

                logger.info(f"Financial data collection complete for {symbol}")

            except Exception as e:
                logger.error(f"Error collecting financial data for {symbol}: {e}")

    def _collect_news(self, task: DataCollectionTask):
        """Collect news for the given task."""
        for symbol in task.company_symbols:
            try:
                company_dir = self._get_company_dir(symbol)

                # Get company profile to have the company name
                profile = get_company_profile(symbol)
                company_name = profile.name if profile else symbol

                # Get news from both sources
                all_news = []

                # 1. Yahoo Finance News (free)
                yahoo_news = get_yahoo_finance_news(symbol)
                if yahoo_news:
                    # Validate the news
                    validation_report = validate_news_articles(yahoo_news, symbol)
                    self.last_validation[f"yahoo_news_{symbol}"] = validation_report
                    all_news.extend(yahoo_news)

                # 2. News API (if key is available)
                news_api_articles = get_company_news(symbol, company_name)
                if news_api_articles:
                    # Validate the news
                    validation_report = validate_news_articles(
                        news_api_articles, symbol
                    )
                    self.last_validation[f"news_api_{symbol}"] = validation_report
                    all_news.extend(news_api_articles)

                if all_news:
                    # Save news to CSV
                    news_file = os.path.join(company_dir, "news_articles.csv")
                    news_df = pd.DataFrame(
                        [
                            {
                                "title": article.title,
                                "publication": article.publication,
                                "date": (
                                    article.date.isoformat() if article.date else None
                                ),
                                "url": article.url,
                                "summary": article.summary,
                                "sentiment": article.sentiment,
                                "is_valid": article.relevance_score
                                is not None,  # Use relevance as validation
                            }
                            for article in all_news
                        ]
                    )
                    news_df.to_csv(news_file, index=False)

                    # Save full article content separately
                    articles_dir = os.path.join(company_dir, "articles")
                    os.makedirs(articles_dir, exist_ok=True)

                    for i, article in enumerate(all_news):
                        if article.content:
                            article_filename = (
                                f"article_{article.date.strftime('%Y%m%d')}_{i}.txt"
                            )
                            with open(
                                os.path.join(articles_dir, article_filename), "w"
                            ) as f:
                                f.write(f"Title: {article.title}\n")
                                f.write(f"Source: {article.publication}\n")
                                f.write(
                                    f"Date: {article.date.isoformat() if article.date else 'Unknown'}\n"
                                )
                                f.write(f"URL: {article.url}\n\n")
                                f.write(article.content)

                logger.info(
                    f"News collection complete for {symbol}: {len(all_news)} articles"
                )

            except Exception as e:
                logger.error(f"Error collecting news for {symbol}: {e}")

    def _collect_sec_filings(self, task: DataCollectionTask):
        """Collect SEC filings for the given task."""
        for symbol in task.company_symbols:
            try:
                company_dir = self._get_company_dir(symbol)
                filings_dir = os.path.join(company_dir, "sec_filings")
                os.makedirs(filings_dir, exist_ok=True)

                # Get recent filings
                filings = get_recent_filings(symbol)

                if filings:
                    # Save filings metadata
                    filings_file = os.path.join(company_dir, "sec_filings_metadata.csv")
                    filings_df = pd.DataFrame(
                        [
                            {
                                "filing_type": filing.filing_type,
                                "filing_date": filing.filing_date.isoformat(),
                                "accession_number": filing.accession_number,
                                "url": filing.url,
                            }
                            for filing in filings
                        ]
                    )
                    filings_df.to_csv(filings_file, index=False)

                    # Download content for important filings
                    important_filings = ["10-K", "10-Q"]
                    for filing in filings:
                        if filing.filing_type in important_filings:
                            # Download filing document
                            content = download_filing_document(filing)
                            if content:
                                # Save content to file
                                filing_filename = f"{filing.filing_type}_{filing.filing_date.strftime('%Y%m%d')}.txt"
                                with open(
                                    os.path.join(filings_dir, filing_filename),
                                    "w",
                                    encoding="utf-8",
                                ) as f:
                                    f.write(content)

                logger.info(
                    f"SEC filings collection complete for {symbol}: {len(filings)} filings"
                )

            except Exception as e:
                logger.error(f"Error collecting SEC filings for {symbol}: {e}")

    def _get_company_dir(self, symbol: str) -> str:
        """Get the directory for a company's data."""
        company_dir = os.path.join(self.output_dir, symbol)
        os.makedirs(company_dir, exist_ok=True)
        return company_dir

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a summary of the latest validation results."""
        if not self.last_validation:
            return {"status": "No validation data available"}

        # Generate combined report from all validation reports
        reports = list(self.last_validation.values())
        return generate_combined_report(reports)

    def collect_all_data_for_symbol(self, symbol: str):
        """
        Perform an immediate full data collection for a symbol.

        Args:
            symbol: Stock ticker symbol to collect data for
        """
        logger.info(f"Starting full data collection for {symbol}")

        # Add the company if not already monitored
        if symbol not in self.symbols_monitored:
            self.add_company(symbol)

        # Execute each type of collection task
        market_task = DataCollectionTask(
            task_name=f"market_data_{symbol}",
            data_type="market_data",
            company_symbols=[symbol],
        )
        self._collect_market_data(market_task)

        financial_task = DataCollectionTask(
            task_name=f"financial_data_{symbol}",
            data_type="financial_statements",
            company_symbols=[symbol],
        )
        self._collect_financial_data(financial_task)

        news_task = DataCollectionTask(
            task_name=f"news_{symbol}", data_type="news", company_symbols=[symbol]
        )
        self._collect_news(news_task)

        sec_task = DataCollectionTask(
            task_name=f"sec_filings_{symbol}",
            data_type="sec_filings",
            company_symbols=[symbol],
        )
        self._collect_sec_filings(sec_task)

        logger.info(f"Full data collection complete for {symbol}")

        # Return validation summary
        return self.get_validation_summary()
