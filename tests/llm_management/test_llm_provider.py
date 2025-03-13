"""
Tests for the LLM provider module.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from tumkwe_invest.llm_management import LLMProvider, get_llm_provider
from tumkwe_invest.llm_management.llm_provider import LLMManager


class TestLLMProvider(unittest.TestCase):
    """
    Test case for the LLM provider functions.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Save any existing API keys to restore later
        self.original_openai_key = os.environ.get("OPENAI_API_KEY")
        self.original_anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        self.original_groq_key = os.environ.get("GROQ_API_KEY")
        
        # Clear environment variables for testing
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]
        if "GROQ_API_KEY" in os.environ:
            del os.environ["GROQ_API_KEY"]
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Restore original API keys
        if self.original_openai_key:
            os.environ["OPENAI_API_KEY"] = self.original_openai_key
        elif "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
            
        if self.original_anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = self.original_anthropic_key
        elif "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]
            
        if self.original_groq_key:
            os.environ["GROQ_API_KEY"] = self.original_groq_key
        elif "GROQ_API_KEY" in os.environ:
            del os.environ["GROQ_API_KEY"]
    
    @patch("tumkwe_invest.llm_management.llm_provider.ChatOpenAI")
    def test_get_openai_provider(self, mock_openai):
        """Test getting an OpenAI provider."""
        # Set up mock
        mock_instance = MagicMock()
        mock_openai.return_value = mock_instance
        
        # Get the provider
        provider = get_llm_provider("openai", api_key="test-api-key")
        
        # Verify ChatOpenAI was called with expected args
        mock_openai.assert_called_once()
        self.assertEqual(os.environ.get("OPENAI_API_KEY"), "test-api-key")
        self.assertEqual(provider, mock_instance)

    @patch("tumkwe_invest.llm_management.llm_provider.ChatAnthropic")
    def test_get_anthropic_provider(self, mock_anthropic):
        """Test getting an Anthropic provider."""
        # Set up mock
        mock_instance = MagicMock()
        mock_anthropic.return_value = mock_instance
        
        # Get the provider
        provider = get_llm_provider(
            LLMProvider.ANTHROPIC, 
            api_key="test-api-key", 
            model="claude-3-opus"
        )
        
        # Verify ChatAnthropic was called with expected args
        mock_anthropic.assert_called_once_with(
            model="claude-3-opus", 
            temperature=0.0
        )
        self.assertEqual(os.environ.get("ANTHROPIC_API_KEY"), "test-api-key")
        self.assertEqual(provider, mock_instance)

    @patch("tumkwe_invest.llm_management.llm_provider.ChatGroq")
    def test_get_groq_provider(self, mock_groq):
        """Test getting a Groq provider."""
        # Set up mock
        mock_instance = MagicMock()
        mock_groq.return_value = mock_instance
        
        # Get the provider
        provider = get_llm_provider(
            "groq", 
            api_key="test-api-key", 
            temperature=0.7
        )
        
        # Verify ChatGroq was called with expected args
        mock_groq.assert_called_once_with(
            model="llama3-8b-8192", 
            temperature=0.7
        )
        self.assertEqual(os.environ.get("GROQ_API_KEY"), "test-api-key")
        self.assertEqual(provider, mock_instance)

    @patch("tumkwe_invest.llm_management.llm_provider.ChatOllama")
    def test_get_ollama_provider(self, mock_ollama):
        """Test getting an Ollama provider."""
        # Set up mock
        mock_instance = MagicMock()
        mock_ollama.return_value = mock_instance
        
        # Get the provider
        provider = get_llm_provider("ollama", model="mistral")
        
        # Verify ChatOllama was called with expected args
        mock_ollama.assert_called_once_with(model="mistral", temperature=0.0)
        self.assertEqual(provider, mock_instance)

    def test_unsupported_provider(self):
        """Test an unsupported provider."""
        with self.assertRaises(ValueError):
            get_llm_provider("unsupported_provider")

    def test_provider_enum_from_string(self):
        """Test parsing provider enum from string."""
        self.assertEqual(LLMProvider("openai"), LLMProvider.OPENAI)
        self.assertEqual(LLMProvider("anthropic"), LLMProvider.ANTHROPIC)
        self.assertEqual(LLMProvider("groq"), LLMProvider.GROQ)
        self.assertEqual(LLMProvider("ollama"), LLMProvider.OLLAMA)

    @patch("tumkwe_invest.llm_management.llm_provider.get_llm_provider")
    def test_llm_manager_init(self, mock_get_provider):
        """Test LLMManager initialization."""
        # Set up mock
        mock_instance = MagicMock()
        mock_get_provider.return_value = mock_instance
        
        # Create manager
        manager = LLMManager(
            provider="openai", 
            api_key="test-key", 
            model="gpt-4", 
            temperature=0.5
        )
        
        # Verify get_llm_provider was called with expected args
        mock_get_provider.assert_called_once_with(
            provider="openai",
            api_key="test-key",
            model="gpt-4",
            temperature=0.5
        )
        self.assertEqual(manager.llm, mock_instance)

    @patch("tumkwe_invest.llm_management.llm_provider.get_llm_provider")
    def test_llm_manager_change_provider(self, mock_get_provider):
        """Test changing provider in LLMManager."""
        # Set up mocks for initial provider and changed provider
        mock_instance1 = MagicMock()
        mock_instance2 = MagicMock()
        mock_get_provider.side_effect = [mock_instance1, mock_instance2]
        
        # Create manager and change provider
        manager = LLMManager(provider="openai")
        self.assertEqual(manager.llm, mock_instance1)
        
        manager.change_provider(
            provider="anthropic",
            api_key="new-key",
            model="claude-3"
        )
        
        # Verify get_llm_provider was called with expected args for new provider
        self.assertEqual(mock_get_provider.call_count, 2)
        mock_get_provider.assert_called_with(
            provider="anthropic",
            api_key="new-key",
            model="claude-3",
            temperature=0.0
        )
        self.assertEqual(manager.llm, mock_instance2)


class TestLLMProviderIntegration(unittest.TestCase):
    """
    Integration tests for the LLM provider functions.
    
    These tests are skipped by default since they require API keys.
    """
    
    def test_openai_integration(self):
        """Test actual OpenAI integration."""
        if not os.environ.get("OPENAI_API_KEY"):
            self.skipTest("OpenAI API key not available")
        
        llm = get_llm_provider(LLMProvider.OPENAI)
        result = llm.invoke("What is the capital of France?")
        self.assertIn("Paris", result.content)
    
    def test_anthropic_integration(self):
        """Test actual Anthropic integration."""
        if not os.environ.get("ANTHROPIC_API_KEY"):
            self.skipTest("Anthropic API key not available")
        
        llm = get_llm_provider(LLMProvider.ANTHROPIC)
        result = llm.invoke("What is the capital of Germany?")
        self.assertIn("Berlin", result.content)
    
    def test_groq_integration(self):
        """Test actual Groq integration."""
        if not os.environ.get("GROQ_API_KEY"):
            self.skipTest("Groq API key not available")
        
        llm = get_llm_provider(LLMProvider.GROQ)
        result = llm.invoke("What is the capital of Japan?")
        self.assertIn("Tokyo", result.content)
    
    @unittest.skip("Requires local Ollama server")
    def test_ollama_integration(self):
        """Test actual Ollama integration."""
        llm = get_llm_provider(LLMProvider.OLLAMA, model="llama3")
        result = llm.invoke("What is the capital of Italy?")
        self.assertIn("Rome", result.content)


if __name__ == "__main__":
    unittest.main()
