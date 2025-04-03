# Tumkwe Invest

An intelligent investment analysis platform that uses agent-based workflows to provide comprehensive stock market insights.

## Overview

Tumkwe Invest is a Python package designed to help investors make data-driven decisions by collecting and analyzing financial data from various sources. The platform uses specialized agents and intelligent routing to provide investment insights and recommendations.

## Features

- **Data Sources**:

  - Yahoo Finance integration for stock data
  - Company news and articles
  - Sector and industry information
- **Agent-Based Architecture**:

  - Intelligent routing between specialized agents
  - Single-step agent workflows for direct queries
  - Multi-step agent workflows for complex analyses
  - Automated planning and execution of investment research tasks
  - LangGraph orchestration for reliable agent coordination
- **Specialized Agents**:

  - News agent for retrieving and analyzing news articles
  - Sector agent for industry and sector analysis
  - Ticker agent for stock-specific information
  - General agent for handling conversation and other queries
- **LLM Integration**:

  - Support for local LLMs through Ollama
  - LangChain integration for tool use and structured outputs

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/tumkwe-invest.git
cd tumkwe-invest

# Install dependencies
pip install -e .
```

## Getting Started

Make sure to have Ollama running with the Llama 3 model available:

```bash
# Start Ollama with Llama 3 model
ollama run llama3.3
```

## Usage Examples

### Single-Step Agent Workflow

For handling straightforward queries that can be addressed by a single specialized agent:

```python
from tumkwe_invest.single_step_agents import graph, stream_graph_updates

# Simple query that will be routed to the appropriate agent
query = "What are the latest news about Tesla?"
config = {"configurable": {"thread_id": "example-thread-1"}}

# Process the query and get response
stream_graph_updates(query, config)
```

### Multi-Step Agent Workflow

For complex queries requiring multiple steps and different agent capabilities:

```python
from tumkwe_invest.multi_step_agents import graph, stream_graph_updates

# Complex query requiring multiple steps
query = "Analyze Apple's recent performance, including stock price trends, latest news, and how it compares to the tech sector as a whole."
config = {"configurable": {"thread_id": "example-thread-2"}}

# Process the complex query
stream_graph_updates(query, config)
```

### Using Specific Agents Directly

If you want to interact with a specific agent directly:

```python
from langchain_core.messages import HumanMessage
from tumkwe_invest.single_step_agents import llm_ticker, llm_news, llm_sector

# Ticker agent for stock information
ticker_response = llm_ticker.invoke([
    HumanMessage(content="What's the current price of AAPL?")
])
print(ticker_response.content)

# News agent for company news
news_response = llm_news.invoke([
    HumanMessage(content="Find recent news about Microsoft's AI investments")
])
print(news_response.content)

# Sector agent for industry analysis
sector_response = llm_sector.invoke([
    HumanMessage(content="How is the semiconductor industry performing this quarter?")
])
print(sector_response.content)
```

### Interactive Chat Interface

For an interactive command-line interface:

```python
from tumkwe_invest.single_step_agents import stream_graph_updates

# Configuration
config = {"configurable": {"thread_id": "my-investment-chat"}}

print("Welcome to Tumkwe Invest! Type 'exit' to quit.")
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit", "q"]:
        break
    stream_graph_updates(user_input, config)
```

## Project Structure

```
tumkwe_invest/
├── __init__.py
├── single_step_agents.py     # Single-request, single-agent workflow
├── multi_step_agents.py      # Complex query planning and execution
├── news                      # News retrieval and analysis tools
├── sector                    # Industry and sector analysis tools
├── ticker                    # Stock ticker specific tools
```

## Configuration

```python
from langchain_ollama import ChatOllama
from tumkwe_invest.single_step_agents import news_tools, sector_tools, ticker_tools

# Configure with different model and temperature
custom_llm = ChatOllama(model="llama3:70b", temperature=0.7)

# Create tool-bound instances for your application
custom_news_agent = custom_llm.bind_tools(tools=news_tools)
custom_sector_agent = custom_llm.bind_tools(tools=sector_tools)
custom_ticker_agent = custom_llm.bind_tools(tools=ticker_tools)
```
