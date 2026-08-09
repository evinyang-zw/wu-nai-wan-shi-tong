import pytest
from unittest.mock import patch, MagicMock
from src.llm.factory import create_llm_provider
from src.llm.base import LLMProviderError, LLMProvider
from src.llm.openai_provider import OpenAIProvider
from src.llm.anthropic_provider import AnthropicProvider


class TestCreateLLMProvider:
    def test_create_openai_provider(self):
        """Test creating OpenAI provider with default parameters."""
        with patch("src.llm.openai_provider.AsyncOpenAI"):
            provider = create_llm_provider("openai", api_key="test-key")
            assert isinstance(provider, OpenAIProvider)
            assert provider._model == "gpt-4o"

    def test_create_anthropic_provider(self):
        """Test creating Anthropic provider with default parameters."""
        with patch("src.llm.anthropic_provider.AsyncAnthropic"):
            provider = create_llm_provider("anthropic", api_key="test-key")
            assert isinstance(provider, AnthropicProvider)
            assert provider._model == "claude-sonnet-4-20250514"

    def test_create_with_model(self):
        """Test creating providers with custom model names."""
        with patch("src.llm.openai_provider.AsyncOpenAI"):
            provider = create_llm_provider("openai", api_key="test-key", model="gpt-3.5-turbo")
            assert isinstance(provider, OpenAIProvider)
            assert provider._model == "gpt-3.5-turbo"

        with patch("src.llm.anthropic_provider.AsyncAnthropic"):
            provider = create_llm_provider(
                "anthropic", api_key="test-key", model="claude-3-opus-20240229"
            )
            assert isinstance(provider, AnthropicProvider)
            assert provider._model == "claude-3-opus-20240229"

    def test_unknown_provider(self):
        """Test that unknown provider falls back to OpenAI-compatible API."""
        with patch("src.llm.openai_provider.AsyncOpenAI"):
            provider = create_llm_provider("unknown", api_key="test-key", base_url="https://api.example.com/v1")
            assert isinstance(provider, OpenAIProvider)

    def test_create_returns_llm_provider_instance(self):
        """Test that created providers are instances of LLMProvider."""
        with patch("src.llm.openai_provider.AsyncOpenAI"):
            provider = create_llm_provider("openai", api_key="test-key")
            assert isinstance(provider, LLMProvider)

        with patch("src.llm.anthropic_provider.AsyncAnthropic"):
            provider = create_llm_provider("anthropic", api_key="test-key")
            assert isinstance(provider, LLMProvider)