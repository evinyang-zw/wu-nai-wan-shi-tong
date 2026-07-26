from __future__ import annotations
from typing import Any
from src.llm.base import LLMProvider, LLMProviderError


def create_llm_provider(provider_name: str, **kwargs: Any) -> LLMProvider:
    if provider_name == "openai":
        from src.llm.openai_provider import OpenAIProvider
        return OpenAIProvider(**kwargs)
    elif provider_name == "anthropic":
        from src.llm.anthropic_provider import AnthropicProvider
        return AnthropicProvider(**kwargs)
    else:
        raise LLMProviderError(f"不支持的 LLM 提供商: {provider_name}，支持的提供商: openai, anthropic")