"""
Module for collecting and analyzing news using LangChain agents and Yahoo Finance.
"""

from typing import Dict, List, Optional, Union

from langchain.agents import AgentType, initialize_agent
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool

from tumkwe_invest.llm_management import LLMProvider, get_llm_provider


class LangChainNewsAnalyzer:
    """
    A class that uses LangChain agents with Yahoo Finance to analyze news for stocks.
    """

    def __init__(
        self,
        provider: Union[str, LLMProvider] = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        verbose: bool = False,
        **kwargs
    ):
        """
        Initialize the LangChain News Analyzer.

        Args:
            provider: LLM provider (openai, anthropic, groq, ollama)
            api_key: API key for the provider (if None, will try to use environment variables)
            model: Model name to use (if None, will use provider defaults)
            temperature: Temperature for generation (0.0 = deterministic)
            verbose: Whether to print debug information for the agent
            **kwargs: Additional arguments to pass to the LLM provider
        """
        self.llm = get_llm_provider(
            provider=provider,
            api_key=api_key,
            model=model,
            temperature=temperature,
            **kwargs
        )

        self.tools = [YahooFinanceNewsTool()]
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=verbose,
        )

    def get_stock_news(self, ticker: str) -> str:
        """
        Get the latest news for a specific stock ticker.

        Args:
            ticker: The stock ticker symbol (e.g., 'AAPL', 'MSFT')

        Returns:
            String containing the latest news.
        """
        tool = YahooFinanceNewsTool()
        return tool.invoke(ticker)

    def analyze_stock_news(self, query: str) -> str:
        """
        Analyze stock news based on a natural language query.

        Args:
            query: Natural language query about stock news

        Returns:
            Analysis results as a string
        """
        return self.agent.invoke(query)["output"]

    def compare_stocks(self, tickers: List[str]) -> Dict[str, str]:
        """
        Get news for multiple stock tickers.

        Args:
            tickers: List of stock ticker symbols

        Returns:
            Dictionary mapping tickers to their news
        """
        results = {}
        for ticker in tickers:
            results[ticker] = self.get_stock_news(ticker)
        return results

    def change_llm_provider(
        self,
        provider: Union[str, LLMProvider],
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> None:
        """
        Change the LLM provider being used by the news analyzer.

        Args:
            provider: New LLM provider
            api_key: API key for the new provider
            model: Model name for the new provider
            temperature: Temperature setting for the new provider
            **kwargs: Additional arguments for the new provider
        """
        # Keep existing temperature if not specified
        if temperature is None:
            temperature = (
                self.llm.temperature if hasattr(self.llm, "temperature") else 0.0
            )

        # Create new LLM
        self.llm = get_llm_provider(
            provider=provider,
            api_key=api_key,
            model=model,
            temperature=temperature,
            **kwargs
        )

        # Reinitialize the agent with the new LLM
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=self.agent.verbose,
        )
