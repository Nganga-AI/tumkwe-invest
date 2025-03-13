"""
Tests for the LangChain news analyzer.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from tumkwe_invest.datacollection.collectors.langchain_news import LangChainNewsAnalyzer
from tumkwe_invest.llm_management import LLMProvider


class TestLangChainNewsAnalyzer(unittest.TestCase):
    """
    Test case for the LangChain news analyzer.
    """
    
    @patch("tumkwe_invest.datacollection.collectors.langchain_news.get_llm_provider")
    @patch("tumkwe_invest.datacollection.collectors.langchain_news.initialize_agent")
    def setUp(self, mock_initialize_agent, mock_get_llm_provider):
        """Set up test fixtures."""
        # Set up mocks
        self.mock_llm = MagicMock()
        self.mock_agent = MagicMock()
        mock_get_llm_provider.return_value = self.mock_llm
        mock_initialize_agent.return_value = self.mock_agent
        
        # Create analyzer
        self.analyzer = LangChainNewsAnalyzer(
            provider="openai",
            api_key="test-key",
            model="test-model"
        )
        
        # Verify initialization
        mock_get_llm_provider.assert_called_once_with(
            provider="openai",
            api_key="test-key",
            model="test-model",
            temperature=0.0
        )
        mock_initialize_agent.assert_called_once()
    
    @patch("tumkwe_invest.datacollection.collectors.langchain_news.YahooFinanceNewsTool")
    def test_get_stock_news(self, mock_yahoo_tool):
        """Test getting stock news."""
        # Set up mock
        mock_tool_instance = MagicMock()
        mock_tool_instance.invoke.return_value = "Apple news: Stock up 2%"
        mock_yahoo_tool.return_value = mock_tool_instance
        
        # Get news
        news = self.analyzer.get_stock_news("AAPL")
        
        # Verify
        mock_yahoo_tool.assert_called_once()
        mock_tool_instance.invoke.assert_called_once_with("AAPL")
        self.assertEqual(news, "Apple news: Stock up 2%")
    
    def test_analyze_stock_news(self):
        """Test analyzing stock news."""
        # Set up mock
        self.mock_agent.invoke.return_value = {"output": "Microsoft stock analysis"}
        
        # Analyze news
        analysis = self.analyzer.analyze_stock_news("What happened with MSFT?")
        
        # Verify
        self.mock_agent.invoke.assert_called_once_with("What happened with MSFT?")
        self.assertEqual(analysis, "Microsoft stock analysis")
    
    @patch("tumkwe_invest.datacollection.collectors.langchain_news.YahooFinanceNewsTool")
    def test_compare_stocks(self, mock_yahoo_tool):
        """Test comparing stocks."""
        # Set up mock
        mock_tool_instance = MagicMock()
        mock_tool_instance.invoke.side_effect = [
            "Apple news: Stock up 2%",
            "Google news: New product launch",
            "Microsoft news: Azure growth"
        ]
        mock_yahoo_tool.return_value = mock_tool_instance
        
        # Compare stocks
        results = self.analyzer.compare_stocks(["AAPL", "GOOGL", "MSFT"])
        
        # Verify
        self.assertEqual(mock_tool_instance.invoke.call_count, 3)
        self.assertEqual(results, {
            "AAPL": "Apple news: Stock up 2%",
            "GOOGL": "Google news: New product launch",
            "MSFT": "Microsoft news: Azure growth"
        })
    
    @patch("tumkwe_invest.datacollection.collectors.langchain_news.get_llm_provider")
    @patch("tumkwe_invest.datacollection.collectors.langchain_news.initialize_agent")
    def test_change_llm_provider(self, mock_initialize_agent, mock_get_llm_provider):
        """Test changing the LLM provider."""
        # Set up mocks for new LLM and agent
        new_mock_llm = MagicMock()
        new_mock_agent = MagicMock()
        mock_get_llm_provider.return_value = new_mock_llm
        mock_initialize_agent.return_value = new_mock_agent
        
        # Change provider
        self.analyzer.change_llm_provider(
            provider=LLMProvider.ANTHROPIC,
            api_key="new-key",
            model="claude-3"
        )
        
        # Verify
        mock_get_llm_provider.assert_called_once_with(
            provider=LLMProvider.ANTHROPIC,
            api_key="new-key",
            model="claude-3",
            temperature=0.0
        )
        mock_initialize_agent.assert_called_once()
        self.assertEqual(self.analyzer.llm, new_mock_llm)
        self.assertEqual(self.analyzer.agent, new_mock_agent)


class TestLangChainNewsAnalyzerIntegration(unittest.TestCase):
    """
    Integration tests for the LangChain news analyzer.
    
    These tests are skipped by default since they require API keys.
    """
    
    def test_news_retrieval(self):
        """Test actual news retrieval."""
        self.skipTest("Integration test requiring API keys")
        analyzer = LangChainNewsAnalyzer()
        news = analyzer.get_stock_news("AAPL")
        self.assertGreater(len(news), 0)  # Should get some news content
    
    def test_news_analysis(self):
        """Test actual news analysis."""
        self.skipTest("Integration test requiring API keys")
        analyzer = LangChainNewsAnalyzer()
        analysis = analyzer.analyze_stock_news("What happened with Apple stock today?")
        self.assertGreater(len(analysis), 0)  # Should get some analysis


if __name__ == "__main__":
    unittest.main()
