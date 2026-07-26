from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_anthropic_client():
    with patch("src.llm.anthropic_provider.AsyncAnthropic") as MockClient:
        client = MockClient.return_value
        client.messages = MagicMock()
        client.messages.create = AsyncMock()
        yield client


@pytest.fixture
def provider(mock_anthropic_client):
    from src.llm.anthropic_provider import AnthropicProvider

    return AnthropicProvider(api_key="test-key", model="claude-sonnet-4-20250514")


class TestFormatToolResult:
    def test_format_tool_result(self, provider):
        result = provider.format_tool_result(tool_call_id="call_123", result='{"answer": 42}')
        assert result == {
            "role": "user",
            "content": [{"type": "tool_result", "tool_use_id": "call_123", "content": '{"answer": 42}'}],
        }


class TestChatWithToolsTextResponse:
    async def test_text_response(self, provider, mock_anthropic_client):
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "Hello, I can help with that."

        mock_response = MagicMock()
        mock_response.content = [text_block]
        mock_anthropic_client.messages.create.return_value = mock_response

        messages = [{"role": "user", "content": "Hi"}]
        response = await provider.chat_with_tools(messages=messages, tools=[])

        assert response.content == "Hello, I can help with that."
        assert response.tool_calls is None
        assert response.raw_message["role"] == "assistant"
        mock_anthropic_client.messages.create.assert_called_once()

    async def test_system_message_extracted(self, provider, mock_anthropic_client):
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "OK"

        mock_response = MagicMock()
        mock_response.content = [text_block]
        mock_anthropic_client.messages.create.return_value = mock_response

        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hi"},
        ]
        await provider.chat_with_tools(messages=messages, tools=[])

        call_kwargs = mock_anthropic_client.messages.create.call_args[1]
        assert call_kwargs["system"] == "You are helpful."
        assert call_kwargs["messages"] == [{"role": "user", "content": "Hi"}]


class TestChatWithToolsToolCall:
    async def test_tool_call_response(self, provider, mock_anthropic_client):
        tool_block = MagicMock()
        tool_block.type = "tool_use"
        tool_block.id = "call_abc"
        tool_block.name = "get_weather"
        tool_block.input = {"city": "Beijing"}

        mock_response = MagicMock()
        mock_response.content = [tool_block]
        mock_anthropic_client.messages.create.return_value = mock_response

        messages = [{"role": "user", "content": "Weather in Beijing?"}]
        tools = [{"name": "get_weather", "description": "Get weather", "input_schema": {}}]
        response = await provider.chat_with_tools(messages=messages, tools=tools)

        assert response.content is None
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].id == "call_abc"
        assert response.tool_calls[0].name == "get_weather"
        assert response.tool_calls[0].arguments == {"city": "Beijing"}

    async def test_mixed_response(self, provider, mock_anthropic_client):
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "Let me check the weather."

        tool_block = MagicMock()
        tool_block.type = "tool_use"
        tool_block.id = "call_def"
        tool_block.name = "get_weather"
        tool_block.input = {"city": "Shanghai"}

        mock_response = MagicMock()
        mock_response.content = [text_block, tool_block]
        mock_anthropic_client.messages.create.return_value = mock_response

        messages = [{"role": "user", "content": "Weather?"}]
        tools = [{"name": "get_weather", "description": "Get weather", "input_schema": {}}]
        response = await provider.chat_with_tools(messages=messages, tools=tools)

        assert response.content == "Let me check the weather."
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].name == "get_weather"
