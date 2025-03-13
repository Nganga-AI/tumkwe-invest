"""
Module for managing different LLM providers through LangChain.
"""

import os
from enum import Enum
from typing import Optional, Dict, Any, Union, List

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama


class LLMProvider(Enum):
    """
    Enum for supported LLM providers.
    """
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    OLLAMA = "ollama"


def get_llm_provider(
    provider: Union[str, LLMProvider],
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.0,
    **kwargs
) -> BaseChatModel:
    """
    Get a LangChain LLM instance based on the specified provider.
    
    Args:
        provider: LLM provider (openai, anthropic, groq, ollama)
        api_key: API key for the provider (if None, will try to use environment variables)
        model: Model name to use (if None, will use provider defaults)
        temperature: Temperature for generation (0.0 = deterministic)
        **kwargs: Additional arguments to pass to the provider
        
    Returns:
        LangChain LLM instance
        
    Raises:
        ValueError: If the provider is not supported
    """
    if isinstance(provider, str):
        try:
            provider = LLMProvider(provider.lower())
        except ValueError:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    # Set default models if not provided
    default_models = {
        LLMProvider.OPENAI: "gpt-3.5-turbo",
        LLMProvider.ANTHROPIC: "claude-3-sonnet-20240229",
        LLMProvider.GROQ: "llama3-8b-8192",
        LLMProvider.OLLAMA: "llama3",
    }
    
    if model is None:
        model = default_models[provider]
    
    # Handle API key management
    if api_key:
        if provider == LLMProvider.OPENAI:
            os.environ["OPENAI_API_KEY"] = api_key
        elif provider == LLMProvider.ANTHROPIC:
            os.environ["ANTHROPIC_API_KEY"] = api_key
        elif provider == LLMProvider.GROQ:
            os.environ["GROQ_API_KEY"] = api_key
    
    # Create and return the appropriate LLM instance
    if provider == LLMProvider.OPENAI:
        return ChatOpenAI(model=model, temperature=temperature, **kwargs)
    
    elif provider == LLMProvider.ANTHROPIC:
        return ChatAnthropic(model=model, temperature=temperature, **kwargs)
    
    elif provider == LLMProvider.GROQ:
        return ChatGroq(model=model, temperature=temperature, **kwargs)
    
    elif provider == LLMProvider.OLLAMA:
        # Ollama requires different initialization parameters
        return ChatOllama(model=model, temperature=temperature, **kwargs)
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


class LLMManager:
    """
    A class to manage different LLM providers.
    """
    
    def __init__(
        self,
        provider: Union[str, LLMProvider] = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        **kwargs
    ):
        """
        Initialize the LLM Manager.
        
        Args:
            provider: LLM provider name or enum
            api_key: API key for the provider
            model: Model name to use
            temperature: Temperature for generation
            **kwargs: Additional arguments for the LLM
        """
        self.provider_name = provider
        self.model = model
        self.temperature = temperature
        self.api_key = api_key
        self.kwargs = kwargs
        self.llm = get_llm_provider(
            provider=provider,
            api_key=api_key,
            model=model,
            temperature=temperature,
            **kwargs
        )
    
    def get_llm(self) -> BaseChatModel:
        """
        Get the LLM instance.
        
        Returns:
            LangChain LLM instance
        """
        return self.llm
    
    def change_provider(
        self,
        provider: Union[str, LLMProvider],
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> None:
        """
        Change the LLM provider.
        
        Args:
            provider: New provider name or enum
            api_key: API key for the new provider
            model: Model name for the new provider
        """
        self.provider_name = provider
        if api_key:
            self.api_key = api_key
        if model:
            self.model = model
        
        self.llm = get_llm_provider(
            provider=provider,
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            **self.kwargs
        )
