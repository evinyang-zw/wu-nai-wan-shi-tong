from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from src.llm.base import LLMProviderError
from src.llm.openai_provider import OpenAIProvider


def _make_openai_response(content=None, tool_calls=None):
    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    choice = SimpleNamespace(message=message)
    return SimpleNamespace(choices=[choice])


class TestFormatToolResult:
    def test_returns_correct_structure(self):
        provider = OpenAIProvider(api_key="fake", model="gpt-4o")
        result = provider.format_tool_result("call_123", '{"value": 42}')
        assert result == {
            "role": "tool",
            "tool_call_id": "call_123",
            "content": '{"value": 42}',
        }


class TestChatWithTools:
    @pytest.mark.asyncio
    async def test_text_response(self):
        provider = OpenAIProvider(api_key="fake", model="gpt-4o")
        provider._client = AsyncMock()
        provider._client.chat.completions.create.return_value = _make_openai_response(
            content="Hello, how can I help?"
        )

        messages = [{"role": "user", "content": "hi"}]
        resp = await provider.chat_with_tools(messages, [])

        assert resp.content == "Hello, how can I help?"
        assert resp.tool_calls is None
        assert resp.raw_message["role"] == "assistant"
        assert resp.raw_message["content"] == "Hello, how can I help?"
        assert "tool_calls" not in resp.raw_message
        provider._client.chat.completions.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_tool_call_response(self):
        provider = OpenAIProvider(api_key="fake", model="gpt-4o")
        provider._client = AsyncMock()

        fn = SimpleNamespace(name="get_weather", arguments='{"city": "Tokyo"}')
        tc = SimpleNamespace(id="call_abc", function=fn)
        provider._client.chat.completions.create.return_value = _make_openai_response(
            content=None, tool_calls=[tc]
        )

        messages = [{"role": "user", "content": "What's the weather?"}]
        tools = [{"type": "function", "function": {"name": "get_weather"}}]
        resp = await provider.chat_with_tools(messages, tools)

        assert resp.tool_calls is not None
        assert len(resp.tool_calls) == 1
        assert resp.tool_calls[0].id == "call_abc"
        assert resp.tool_calls[0].name == "get_weather"
        assert resp.tool_calls[0].arguments == {"city": "Tokyo"}
        assert resp.raw_message["content"] is None
        assert len(resp.raw_message["tool_calls"]) == 1

    @pytest.mark.asyncio
    async def test_api_error_raises_llm_provider_error(self):
        provider = OpenAIProvider(api_key="fake", model="gpt-4o")
        provider._client = AsyncMock()
        provider._client.chat.completions.create.side_effect = RuntimeError("network error")

        with pytest.raises(LLMProviderError, match="OpenAI API 调用失败"):
            await provider.chat_with_tools([], [])
