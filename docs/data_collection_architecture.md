# Data Collection System Architecture

This document describes the architecture of Tumkwe Invest's financial data collection system.

## Overview

The system is designed to collect, validate, and store financial data from various sources. This data will be used later for analysis and to generate investment advice.

```
+-------------------+     +-------------------+     +-------------------+
|                   |     |                   |     |                   |
|  External Sources |     |  Data             |     |  Local Storage    |
|  (APIs, Web)      | --> |  Collectors       | --> |  (JSON Files,     |
|                   |     |                   |     |   CSV)            |
+-------------------+     +-------------------+     +-------------------+
                                   |
                                   v
                          +-------------------+
                          |                   |
                          |  Data             |
                          |  Validation       |
                          |                   |
                          +-------------------+
```

## Main Components

### 1. Data Models (models.py)

Defines the data structures to store different types of financial information:

- `StockPrice`: Historical stock prices
- `FinancialStatement`: Financial statements (income statement, balance sheet, cash flow)
- `CompanyProfile`: Company information
- `KeyMetrics`: Key financial indicators
- `NewsArticle`: Press articles and news
- `SECFiling`: Documents filed with the SEC

### 2. Specialized Collectors

Modules that connect to different data sources:

- `yahoo_finance.py`: Collects stock prices and financial statements via Yahoo Finance
- `sec_edgar.py`: Collects official documents from the SEC
- `yahoo_news.py`: Collects news via Yahoo Finance
- `news_collector.py`: Collects news via News API
- `financial_metrics.py`: Collects advanced financial indicators

### 3. Data Validation (validation.py)

Checks the quality and consistency of data:

- Detection of outliers in stock prices
- Verification of financial statement consistency
- Validation of dates and periods
- Verification of data completeness

### 4. Collection Manager (collector_manager.py)

Coordinates the collection process:

- Schedules collection tasks at different frequencies
- Manages automatic updates
- Stores data consistently
- Provides validation reports

## Typical Workflow

1. The user specifies stock symbols to monitor
2. The collection manager creates tasks for each data type
3. Specialized collectors retrieve data from different sources
4. The data is validated to detect potential issues
5. Validated data is stored locally in a standardized format
6. Updates are scheduled according to the appropriate frequency

## Constraints and Optimizations

- **API Limits**: The system respects the request limits of free APIs
- **Caching**: Data is cached to reduce API calls
- **Error Tolerance**: Collection errors are logged and don't stop the process
- **Automatic Validation**: Data quality issues are detected and reported

## System Extension

To add a new data source:

1. Create a new collector in the `collectors/` folder
2. Adapt the collected data to existing models
3. Add specific validation rules if necessary
4. Integrate the new collector into the collection manager
