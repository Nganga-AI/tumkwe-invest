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
  - LangChain-powered news analysis
- **Analysis Capabilities**:

  - Technical analysis (price patterns, indicators, volume analysis)
  - Fundamental analysis (financial statements, ratios, valuations)
  - Sentiment analysis (news, social media, market sentiment)
  - Integrated scoring system combining multiple analysis methods
  - AI-powered news sentiment analysis using LangChain and OpenAI
- **LLM Integration**:

  - Support for multiple LLM providers (OpenAI, Anthropic, Groq, Ollama)
  - Unified interface for provider switching
  - LangChain integration for advanced prompt engineering

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
│   │   ├── langchain_news.py
│   │   ├── news_collector.py
│   │   ├── sec_edgar.py
│   │   ├── yahoo_finance.py
│   │   └── yahoo_news.py
│   ├── config.py
│   ├── models.py
│   └── validation.py
├── llm_management/         # LLM provider management
│   ├── __init__.py
│   └── llm_provider.py
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

### Basic Analysis

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

### LangChain News Analysis with Multiple LLM Providers

```python
from tumkwe_invest.datacollection.collectors import LangChainNewsAnalyzer
from tumkwe_invest.llm_management import LLMProvider

# Initialize with OpenAI
news_analyzer = LangChainNewsAnalyzer(
    provider=LLMProvider.OPENAI,
    api_key="your-openai-api-key",
    model="gpt-4"
)

# Get news analysis
analysis = news_analyzer.analyze_stock_news("What happened today with Microsoft stocks?")
print(analysis)

# Switch to Claude (Anthropic)
news_analyzer.change_llm_provider(
    provider=LLMProvider.ANTHROPIC,
    api_key="your-anthropic-api-key",
    model="claude-3-opus-20240229"
)

# Get analysis from Claude
claude_analysis = news_analyzer.analyze_stock_news("Compare NVIDIA and AMD stock performance")
print(claude_analysis)

# Use local Ollama model
news_analyzer.change_llm_provider(
    provider=LLMProvider.OLLAMA,
    model="llama3"  # Make sure this model is available in your Ollama instance
)

ollama_analysis = news_analyzer.analyze_stock_news("What are the recent trends for Tesla stock?")
print(ollama_analysis)
```

### Direct LLM Provider Usage

```python
from tumkwe_invest.llm_management import get_llm_provider, LLMProvider

# Get a specific LLM provider
llm = get_llm_provider(
    provider=LLMProvider.GROQ,
    api_key="your-groq-api-key",
    model="llama3-8b-8192"
)

# Use the LLM directly with LangChain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

prompt = PromptTemplate.from_template("Analyze the following financial news: {news}")
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.invoke({"news": "NVIDIA stock reached new heights after AI announcements"})
print(result["text"])
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
- langchain
- langchain_core
- langchain_community
- langchain_openai
- langchain_anthropic
- langchain_groq
- openai
- anthropic

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
