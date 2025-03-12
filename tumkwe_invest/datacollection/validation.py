"""
Data validation tools to ensure quality and consistency of financial data.
"""

import statistics
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from .config import VALIDATION
from .models import (
    CompanyProfile,
    FinancialStatement,
    KeyMetrics,
    NewsArticle,
    StockPrice,
    ValidationReport,
)


def validate_stock_prices(prices: List[StockPrice], symbol: str) -> ValidationReport:
    """
    Validate a list of stock price data points.

    Args:
        prices: List of StockPrice objects
        symbol: Stock ticker symbol

    Returns:
        ValidationReport with validation results
    """
    report = ValidationReport(
        data_type="stock_prices",
        company_symbol=symbol,
        source="multiple" if not prices else prices[0].source,
        total_records=len(prices),
    )

    if not prices:
        report.issues["empty_dataset"] = ["No price data available"]
        return report

    # Sort by date for sequential checks
    prices = sorted(prices, key=lambda x: x.date)

    # Check for missing dates (excluding weekends/holidays)
    dates = [p.date.date() for p in prices]
    date_range = pd.date_range(start=min(dates), end=max(dates), freq="B")
    missing_dates = set(date_range.date) - set(dates)

    if len(missing_dates) > 0:
        completeness_ratio = len(dates) / len(date_range)
        if completeness_ratio < VALIDATION["min_data_completeness"]:
            report.issues["incomplete_data"] = [
                f"Missing {len(missing_dates)} trading days ({(1-completeness_ratio)*100:.1f}% of expected data)"
            ]

    # Calculate statistics for outlier detection
    closing_prices = [p.close for p in prices]
    mean_price = statistics.mean(closing_prices)
    try:
        std_dev = statistics.stdev(closing_prices)
    except statistics.StatisticsError:
        std_dev = 0

    # Check each price record
    valid_count = 0
    for i, price in enumerate(prices):
        issues = []

        # Check for negative values
        if price.open <= 0 or price.high <= 0 or price.low <= 0 or price.close <= 0:
            issues.append("Negative or zero price values")

        # Check for logical consistency
        if price.low > price.high:
            issues.append("Low price greater than high price")

        if price.open > price.high or price.open < price.low:
            issues.append("Open price outside high-low range")

        if price.close > price.high or price.close < price.low:
            issues.append("Close price outside high-low range")

        # Check for extreme daily changes
        if i > 0:
            prev_price = prices[i - 1]
            daily_change_pct = abs(
                (price.close - prev_price.close) / prev_price.close * 100
            )
            if daily_change_pct > VALIDATION["max_price_change_percent"]:
                issues.append(f"Extreme daily price change: {daily_change_pct:.1f}%")

        # Check for outliers
        if (
            abs(price.close - mean_price) > VALIDATION["max_outlier_std"] * std_dev
            and std_dev > 0
        ):
            issues.append(
                f"Price is an outlier: {price.close:.2f} vs mean {mean_price:.2f}"
            )

        # Mark record as invalid and store issues if any
        if issues:
            date_str = price.date.strftime("%Y-%m-%d")
            report.issues[f"price_{date_str}"] = issues
            price.is_valid = False
            price.validation_warnings = issues
        else:
            valid_count += 1

    # Update validation report
    report.valid_records = valid_count

    return report


def validate_financial_statement(statement: FinancialStatement) -> ValidationReport:
    """
    Validate a financial statement.

    Args:
        statement: FinancialStatement object

    Returns:
        ValidationReport with validation results
    """
    report = ValidationReport(
        data_type=f"financial_statement_{statement.statement_type}",
        company_symbol=statement.symbol,
        source=statement.source,
        total_records=1,
    )

    # Check for missing key metrics based on statement type
    expected_fields = set()

    if statement.statement_type == "income_statement":
        expected_fields = {
            "Total Revenue",
            "Net Income",
            "Operating Income",
            "Gross Profit",
            "EBITDA",
        }
    elif statement.statement_type == "balance_sheet":
        expected_fields = {
            "Total Assets",
            "Total Liabilities",
            "Total Equity",
            "Cash And Cash Equivalents",
            "Total Debt",
        }
    elif statement.statement_type == "cash_flow":
        expected_fields = {
            "Operating Cash Flow",
            "Capital Expenditure",
            "Free Cash Flow",
            "Dividend Paid",
        }

    # Check which expected fields are missing
    data_keys = set(statement.data.keys())
    missing_fields = expected_fields - data_keys

    if missing_fields:
        report.issues["missing_fields"] = [
            f"Missing key fields: {', '.join(missing_fields)}"
        ]
        report.missing_fields = missing_fields

    # Check for potential data issues
    issues = []

    # Check for negative revenue (unlikely in most cases)
    if "Total Revenue" in statement.data and statement.data["Total Revenue"] < 0:
        issues.append("Negative Total Revenue")

    # Check for unreasonable profit margins
    if (
        "Net Income" in statement.data
        and "Total Revenue" in statement.data
        and statement.data["Total Revenue"] > 0
    ):
        profit_margin = statement.data["Net Income"] / statement.data["Total Revenue"]
        if profit_margin > 1 or profit_margin < -1:
            issues.append(f"Unusual profit margin: {profit_margin:.2f}")

    # Balance sheet validation (Assets = Liabilities + Equity)
    if statement.statement_type == "balance_sheet":
        if (
            "Total Assets" in statement.data
            and "Total Liabilities" in statement.data
            and "Total Equity" in statement.data
        ):

            assets = statement.data["Total Assets"]
            liab_equity = (
                statement.data["Total Liabilities"] + statement.data["Total Equity"]
            )

            # Allow small rounding differences (0.5%)
            if abs(assets - liab_equity) / assets > 0.005:
                issues.append(
                    f"Balance sheet equation doesn't balance: Assets={assets:.2f}, Liabilities+Equity={liab_equity:.2f}"
                )

    if issues:
        report.issues["data_quality"] = issues
        statement.is_valid = False
        statement.validation_warnings = issues
    else:
        report.valid_records = 1

    return report


def validate_key_metrics(metrics: KeyMetrics) -> ValidationReport:
    """
    Validate key financial metrics.

    Args:
        metrics: KeyMetrics object

    Returns:
        ValidationReport with validation results
    """
    report = ValidationReport(
        data_type="key_metrics",
        company_symbol=metrics.symbol,
        source=metrics.source,
        total_records=1,
    )

    issues = []

    # P/E ratio checks
    if metrics.pe_ratio is not None:
        if metrics.pe_ratio < 0:
            issues.append(f"Negative P/E ratio: {metrics.pe_ratio:.2f}")
        elif metrics.pe_ratio > VALIDATION["max_pe_ratio"]:
            issues.append(f"Unusually high P/E ratio: {metrics.pe_ratio:.2f}")

    # P/B ratio checks
    if metrics.pb_ratio is not None and metrics.pb_ratio < 0:
        issues.append(f"Negative P/B ratio: {metrics.pb_ratio:.2f}")

    # Dividend yield checks
    if (
        metrics.dividend_yield is not None and metrics.dividend_yield > 0.25
    ):  # 25% yield is very high
        issues.append(
            f"Unusually high dividend yield: {metrics.dividend_yield*100:.2f}%"
        )

    # Return ratio checks
    if metrics.return_on_equity is not None and abs(metrics.return_on_equity) > 1:
        issues.append(f"Extreme ROE: {metrics.return_on_equity*100:.2f}%")

    if metrics.return_on_assets is not None and abs(metrics.return_on_assets) > 0.5:
        issues.append(f"Extreme ROA: {metrics.return_on_assets*100:.2f}%")

    if issues:
        report.issues["metric_quality"] = issues
        metrics.is_valid = False
        metrics.validation_warnings = issues
    else:
        report.valid_records = 1

    return report


def validate_company_profile(profile: CompanyProfile) -> ValidationReport:
    """
    Validate company profile information.

    Args:
        profile: CompanyProfile object

    Returns:
        ValidationReport with validation results
    """
    report = ValidationReport(
        data_type="company_profile",
        company_symbol=profile.symbol,
        source=profile.source,
        total_records=1,
    )

    issues = []

    # Check for critical missing information
    if not profile.name:
        issues.append("Missing company name")

    if not profile.sector:
        issues.append("Missing sector information")

    if not profile.industry:
        issues.append("Missing industry information")

    if not profile.description or len(profile.description) < 20:
        issues.append("Missing or very short company description")

    if issues:
        report.issues["missing_info"] = issues
        profile.is_valid = False
        profile.validation_warnings = issues
    else:
        report.valid_records = 1

    return report


def validate_news_articles(
    articles: List[NewsArticle], symbol: str
) -> ValidationReport:
    """
    Validate a list of news articles.

    Args:
        articles: List of NewsArticle objects
        symbol: Company symbol

    Returns:
        ValidationReport with validation results
    """
    report = ValidationReport(
        data_type="news_articles",
        company_symbol=symbol,
        source="multiple" if not articles else articles[0].publication,
        total_records=len(articles),
    )

    if not articles:
        report.issues["empty_dataset"] = ["No news articles available"]
        return report

    valid_count = 0
    for i, article in enumerate(articles):
        issues = []

        # Check for critical missing information
        if not article.title or len(article.title) < 5:
            issues.append("Missing or very short title")

        if not article.summary or len(article.summary) < 10:
            issues.append("Missing or very short summary")

        if not article.url:
            issues.append("Missing article URL")

        # Check if content is available for sentiment analysis
        if not article.content and i < 10:  # Only flag for the first few articles
            issues.append("Missing article content for sentiment analysis")

        # Add company-relevant check
        if (
            article.title
            and symbol.lower() not in article.title.lower()
            and symbol.lower() not in article.summary.lower()
        ):
            relevance_issue = "Article may not be directly relevant to the company"
            if not any(
                issues
            ):  # Don't add this issue if there are already more serious ones
                issues.append(relevance_issue)

        if issues:
            article_id = f"article_{i+1}"
            report.issues[article_id] = issues
        else:
            valid_count += 1

    # Update validation report
    report.valid_records = valid_count

    return report


def generate_combined_report(reports: List[ValidationReport]) -> Dict[str, Any]:
    """
    Generate a combined validation report from multiple reports.

    Args:
        reports: List of ValidationReport objects

    Returns:
        Dictionary with combined validation statistics
    """
    combined = {
        "timestamp": datetime.now().isoformat(),
        "total_records": sum(r.total_records for r in reports),
        "valid_records": sum(r.valid_records for r in reports),
        "validation_rate": 0.0,
        "issues_by_type": {},
        "data_types": [],
    }

    # Calculate validation rate
    if combined["total_records"] > 0:
        combined["validation_rate"] = (
            combined["valid_records"] / combined["total_records"]
        )

    # Aggregate issues by type
    for report in reports:
        combined["data_types"].append(
            {
                "type": report.data_type,
                "symbol": report.company_symbol,
                "source": report.source,
                "total": report.total_records,
                "valid": report.valid_records,
                "issues_count": sum(len(issues) for issues in report.issues.values()),
            }
        )

        for issue_key, issue_list in report.issues.items():
            if issue_key not in combined["issues_by_type"]:
                combined["issues_by_type"][issue_key] = []

            # Add data type info to each issue
            for issue in issue_list:
                combined["issues_by_type"][issue_key].append(
                    f"{report.data_type} ({report.company_symbol}): {issue}"
                )

    return combined
