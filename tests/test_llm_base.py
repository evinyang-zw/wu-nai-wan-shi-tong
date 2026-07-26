"""Tests for LLM base module."""
from __future__ import annotations

import pytest
from src.llm.base import LLMProvider, LLMProviderError, LLMResponse, ToolCall


class TestToolCall:
    def test_create_tool_call(self):
        tc = ToolCall(id="call_1", name="get_weather", arguments={"city": "Beijing"})
        assert tc.id == "call_1"
        assert tc.name == "get_weather"
        assert tc.arguments == {"city": "Beijing"}

    def test_tool_call_equality(self):
        tc1 = ToolCall(id="1", name="fn", arguments={})
        tc2 = ToolCall(id="1", name="fn", arguments={})
        assert tc1 == tc2

    def test_tool_call_different_id(self):
        tc1 = ToolCall(id="1", name="fn", arguments={})
        tc2 = ToolCall(id="2", name="fn", arguments={})
        assert tc1 != tc2


class TestLLMResponse:
    def test_text_response(self):
        resp = LLMResponse(content="Hello!", tool_calls=None, raw_message={"role": "assistant"})
        assert resp.content == "Hello!"
        assert resp.tool_calls is None
        assert resp.raw_message == {"role": "assistant"}

    def test_tool_call_response(self):
        tc = ToolCall(id="call_1", name="search", arguments={"query": "test"})
        resp = LLMResponse(content=None, tool_calls=[tc], raw_message={"role": "assistant"})
        assert resp.content is None
        assert len(resp.tool_calls) == 1
        assert resp.tool_calls[0].name == "search"


class TestLLMProviderError:
    def test_error_message(self):
        err = LLMProviderError("API key invalid")
        assert str(err) == "API key invalid"
        assert isinstance(err, Exception)


class TestLLMProvider:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            LLMProvider()  # type: ignore[abstract]
