# Tumkwe Invest

An intelligent investment analysis platform that combines technical, fundamental, and sentiment analysis to provide comprehensive stock market insights.

## Overview

Tumkwe Invest is a Python package designed to help investors make data-driven decisions by collecting, analyzing, and interpreting financial data from various sources. The platform integrates multiple analysis techniques to provide holistic investment recommendations.

## Features

- **Data Collection**: Automated collection from multiple financial sources

  - Yahoo Finance data
  - SEC EDGAR filings
  - Financial metrics
  - News articles and sentiment data
- **Analysis Capabilities**:

  - Technical analysis (price patterns, indicators, volume analysis)
  - Fundamental analysis (financial statements, ratios, valuations)
  - Sentiment analysis (news, social media, market sentiment)
  - Integrated scoring system combining multiple analysis methods

## Project Structure

```
tumkwe_invest/
├── data_analysis/          # Analysis modules
│   ├── fundamental_analysis.py
│   ├── integrated_analysis.py
│   ├── sentiment_analysis.py
│   ├── technical_analysis.py
│   └── validation.py
├── datacollection/         # Data collection modules
│   ├── collector_manager.py
│   ├── collectors/         # Specific collectors
│   │   ├── financial_metrics.py
│   │   ├── news_collector.py
│   │   ├── sec_edgar.py
│   │   ├── yahoo_finance.py
│   │   └── yahoo_news.py
│   ├── config.py
│   ├── models.py
│   └── validation.py
```

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/tumkwe-invest.git
cd tumkwe-invest

# Install the package
pip install -e .
```

## Usage

```python
import tumkwe_invest as ti

# Data Collection
collector = ti.datacollection.collector_manager.CollectorManager()
data = collector.collect_data("AAPL")

# Technical Analysis
tech_analysis = ti.data_analysis.technical_analysis.TechnicalAnalyzer()
tech_scores = tech_analysis.analyze(data)

# Fundamental Analysis
fund_analysis = ti.data_analysis.fundamental_analysis.FundamentalAnalyzer()
fund_scores = fund_analysis.analyze(data)

# Sentiment Analysis
sent_analysis = ti.data_analysis.sentiment_analysis.SentimentAnalyzer()
sent_scores = sent_analysis.analyze(data)

# Integrated Analysis
integrated = ti.data_analysis.integrated_analysis.IntegratedAnalyzer()
final_score = integrated.get_composite_score(tech_scores, fund_scores, sent_scores)
recommendation = integrated.get_recommendation(final_score)

print(f"Investment recommendation for AAPL: {recommendation}")
```

## Requirements

- Python 3.8+
- pandas
- numpy
- yfinance
- requests
- nltk
- beautifulsoup4
- scikit-learn

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
