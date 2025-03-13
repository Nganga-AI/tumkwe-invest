"""
tumkwe_invest/
├── data_analysis
│   ├── fundamental_analysis.py
│   ├── __init__.py
│   ├── integrated_analysis.py
│   ├── sentiment_analysis.py
│   ├── technical_analysis.py
│   └── validation.py
├── datacollection
│   ├── collector_manager.py
│   ├── collectors
│   │   ├── financial_metrics.py
│   │   ├── __init__.py
│   │   ├── news_collector.py
│   │   ├── sec_edgar.py
│   │   ├── yahoo_finance.py
│   │   └── yahoo_news.py
│   ├── config.py
│   ├── __init__.py
│   ├── models.py
│   └── validation.py
├── llm_management
│   ├── __init__.py
│   └── llm_provider.py
├── ui
│   ├── __init__.py
│   ├── visualization.py
│   ├── dashboard.py
│   ├── components.py
│   └── utils.py
└── __init__.py

datacollection/
Data collection package for Tumkwe Invest.

data_analysis/
Data analysis package for Tumkwe Invest.
This package provides tools for technical, fundamental, and sentiment analysis
of stock market data, as well as integrated scoring mechanisms.

llm_management/
LLM management package for Tumkwe Invest.
This package provides tools for managing different LLM providers through LangChain.

ui/
User Interface package for Tumkwe Invest.
This package provides components for visualizing data, creating dashboards,
and ensuring a user-friendly experience with both basic and advanced views.
"""

from . import data_analysis, datacollection, llm_management, ui

__all__ = ["data_analysis", "datacollection", "llm_management", "ui"]
