"""
Test cases for LLM provider module.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from tumkwe_invest.llm_management.llm_provider import (
    LLMManager,
    LLMProvider,
    get_llm_provider,
)


class TestLLMProvider(unittest.TestCase):
    """Test cases for the LLM provider enum and provider functions."""

    def test_llm_provider_enum(self):
        """Test that LLMProvider enum has the expected values."""
        self.assertEqual(LLMProvider.OPENAI.value, "openai")
        self.assertEqual(LLMProvider.ANTHROPIC.value, "anthropic")
        self.assertEqual(LLMProvider.GROQ.value, "groq")
        self.assertEqual(LLMProvider.OLLAMA.value, "ollama")

    @patch("tumkwe_invest.llm_management.llm_provider.ChatOpenAI")
    def test_get_openai_provider(self, mock_chat_openai):
        """Test getting an OpenAI provider."""
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance

        result = get_llm_provider("openai", api_key="test_key", model="gpt-4")

        self.assertEqual(result, mock_instance)
        mock_chat_openai.assert_called_once_with(model="gpt-4", temperature=0.0)
        self.assertEqual(os.environ.get("OPENAI_API_KEY"), "test_key")

    @patch("tumkwe_invest.llm_management.llm_provider.ChatAnthropic")
    def test_get_anthropic_provider(self, mock_chat_anthropic):
        """Test getting an Anthropic provider."""
        mock_instance = MagicMock()
        mock_chat_anthropic.return_value = mock_instance

        result = get_llm_provider(
            LLMProvider.ANTHROPIC, api_key="test_key", model="claude-3-opus"
        )

        self.assertEqual(result, mock_instance)
        mock_chat_anthropic.assert_called_once_with(
            model="claude-3-opus", temperature=0.0
        )
        self.assertEqual(os.environ.get("ANTHROPIC_API_KEY"), "test_key")

    @patch("tumkwe_invest.llm_management.llm_provider.ChatGroq")
    def test_get_groq_provider(self, mock_chat_groq):
        """Test getting a Groq provider."""
        mock_instance = MagicMock()
        mock_chat_groq.return_value = mock_instance

        result = get_llm_provider("groq", api_key="test_key", temperature=0.7)

        self.assertEqual(result, mock_instance)
        mock_chat_groq.assert_called_once_with(model="llama3-8b-8192", temperature=0.7)
        self.assertEqual(os.environ.get("GROQ_API_KEY"), "test_key")

    @patch("tumkwe_invest.llm_management.llm_provider.ChatOllama")
    def test_get_ollama_provider(self, mock_chat_ollama):
        """Test getting an Ollama provider."""
        mock_instance = MagicMock()
        mock_chat_ollama.return_value = mock_instance

        result = get_llm_provider(LLMProvider.OLLAMA, temperature=0.5)

        self.assertEqual(result, mock_instance)
        mock_chat_ollama.assert_called_once_with(model="llama3", temperature=0.5)

    def test_get_llm_provider_invalid(self):
        """Test that an invalid provider raises ValueError."""
        with self.assertRaises(ValueError):
            get_llm_provider("invalid_provider")

    def test_get_llm_provider_with_additional_kwargs(self):
        """Test passing additional kwargs to provider."""
        with patch(
            "tumkwe_invest.llm_management.llm_provider.ChatOpenAI"
        ) as mock_chat_openai:
            mock_instance = MagicMock()
            mock_chat_openai.return_value = mock_instance

            get_llm_provider(
                "openai", model="gpt-3.5-turbo", streaming=True, max_tokens=100
            )

            mock_chat_openai.assert_called_once_with(
                model="gpt-3.5-turbo", temperature=0.0, streaming=True, max_tokens=100
            )


class TestLLMManager(unittest.TestCase):
    """Test cases for the LLMManager class."""

    @patch("tumkwe_invest.llm_management.llm_provider.get_llm_provider")
    def test_llm_manager_init(self, mock_get_provider):
        """Test LLMManager initialization."""
        mock_llm = MagicMock()
        mock_get_provider.return_value = mock_llm

        manager = LLMManager(
            provider="openai", api_key="test_key", model="gpt-4", temperature=0.5
        )

        self.assertEqual(manager.provider_name, "openai")
        self.assertEqual(manager.model, "gpt-4")
        self.assertEqual(manager.temperature, 0.5)
        self.assertEqual(manager.api_key, "test_key")
        self.assertEqual(manager.llm, mock_llm)

        mock_get_provider.assert_called_once_with(
            provider="openai", api_key="test_key", model="gpt-4", temperature=0.5
        )

    @patch("tumkwe_invest.llm_management.llm_provider.get_llm_provider")
    def test_llm_manager_get_llm(self, mock_get_provider):
        """Test LLMManager.get_llm()."""
        mock_llm = MagicMock()
        mock_get_provider.return_value = mock_llm

        manager = LLMManager(provider="anthropic")
        result = manager.get_llm()

        self.assertEqual(result, mock_llm)

    @patch("tumkwe_invest.llm_management.llm_provider.get_llm_provider")
    def test_llm_manager_change_provider(self, mock_get_provider):
        """Test LLMManager.change_provider()."""
        mock_llm1 = MagicMock()
        mock_llm2 = MagicMock()
        mock_get_provider.side_effect = [mock_llm1, mock_llm2]

        manager = LLMManager(provider="openai", api_key="key1", model="gpt-4")
        self.assertEqual(manager.llm, mock_llm1)

        manager.change_provider(provider="anthropic", api_key="key2", model="claude-3")

        self.assertEqual(manager.provider_name, "anthropic")
        self.assertEqual(manager.api_key, "key2")
        self.assertEqual(manager.model, "claude-3")
        self.assertEqual(manager.llm, mock_llm2)

        mock_get_provider.assert_called_with(
            provider="anthropic", api_key="key2", model="claude-3", temperature=0.0
        )


if __name__ == "__main__":
    unittest.main()
