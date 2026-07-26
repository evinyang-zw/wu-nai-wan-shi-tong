"""Tests for WanShiTongAgent core conversation loop."""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from src.agent.config import AgentConfig
from src.agent.core import WanShiTongAgent
from src.llm.base import LLMProviderError, LLMResponse, ToolCall
from src.tools.registry import ToolExecutionError, ToolRegistry
from src.schema.types import WeatherParams


# --- helpers ---------------------------------------------------------------

async def weather_executor(params: WeatherParams) -> str:
    return f"{params.city}今天晴，25°C"


def _make_response(
    content: str | None = None,
    tool_calls: list[ToolCall] | None = None,
) -> LLMResponse:
    raw: dict[str, Any] = {"role": "assistant"}
    if content:
        raw["content"] = content
    if tool_calls:
        raw["tool_calls"] = [
            {"id": tc.id, "type": "function", "function": {"name": tc.name, "arguments": tc.arguments}}
            for tc in tool_calls
        ]
    return LLMResponse(content=content, tool_calls=tool_calls, raw_message=raw)


def _build_mock_llm(responses: list[LLMResponse]) -> MagicMock:
    llm = MagicMock()
    llm.chat_with_tools = AsyncMock(side_effect=responses)
    llm.format_tool_result = MagicMock(
        side_effect=lambda tc_id, result: {
            "role": "tool",
            "tool_call_id": tc_id,
            "content": result,
        }
    )
    return llm


def _build_registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register("weather", WeatherParams, "查询天气", weather_executor)
    return reg


# --- tests -----------------------------------------------------------------

class TestSimpleTextResponse:
    @pytest.mark.asyncio
    async def test_simple_text_response(self) -> None:
        """LLM returns text directly — no tool calls."""
        response = _make_response(content="你好！有什么可以帮你的？")
        llm = _build_mock_llm([response])
        agent = WanShiTongAgent(llm=llm, tools=_build_registry())

        result = await agent.chat("你好")

        assert result == "你好！有什么可以帮你的？"
        assert len(agent.conversation_history) == 2
        assert agent.conversation_history[0]["role"] == "user"
        assert agent.conversation_history[1]["role"] == "assistant"


class TestSingleToolCall:
    @pytest.mark.asyncio
    async def test_single_tool_call(self) -> None:
        """LLM calls a tool once, then returns final answer."""
        tool_call = ToolCall(id="call_1", name="weather", arguments={"city": "北京"})
        tool_response = _make_response(tool_calls=[tool_call])
        final_response = _make_response(content="北京今天晴，25°C。")

        llm = _build_mock_llm([tool_response, final_response])
        agent = WanShiTongAgent(llm=llm, tools=_build_registry())

        result = await agent.chat("北京天气怎么样")

        assert result == "北京今天晴，25°C。"
        # history: user -> assistant(tool_call) -> tool -> assistant(final)
        assert len(agent.conversation_history) == 4
        assert agent.conversation_history[2]["role"] == "tool"
        # LLM was called twice: once with tool call, once to get final answer
        assert llm.chat_with_tools.call_count == 2


class TestMaxRoundsExceeded:
    @pytest.mark.asyncio
    async def test_max_rounds_exceeded(self) -> None:
        """Agent stops after max_tool_rounds when LLM keeps requesting tools."""
        tool_call = ToolCall(id="call_n", name="weather", arguments={"city": "上海"})
        always_tool = _make_response(tool_calls=[tool_call])

        config = AgentConfig(max_tool_rounds=3)
        llm = _build_mock_llm([always_tool, always_tool, always_tool])
        agent = WanShiTongAgent(llm=llm, tools=_build_registry(), config=config)

        result = await agent.chat("上海天气")

        assert "抱歉" in result
        assert llm.chat_with_tools.call_count == 3


class TestToolExecutionError:
    @pytest.mark.asyncio
    async def test_tool_execution_error(self) -> None:
        """Tool fails — error message is passed back to LLM."""
        tool_call = ToolCall(id="call_fail", name="weather", arguments={"city": "北京"})
        tool_response = _make_response(tool_calls=[tool_call])
        final_response = _make_response(content="查询出错了。")

        llm = _build_mock_llm([tool_response, final_response])
        agent = WanShiTongAgent(llm=llm, tools=_build_registry())

        # Patch the executor to raise ToolExecutionError
        async def failing_executor(params: Any) -> str:
            raise ToolExecutionError("weather", "网络超时")

        agent.tools._tools["weather"].executor = failing_executor

        result = await agent.chat("北京天气")

        assert result == "查询出错了。"
        # The tool error message should be in the conversation history
        tool_msg = agent.conversation_history[2]
        assert tool_msg["role"] == "tool"
        assert "网络超时" in tool_msg["content"]


class TestLLMProviderError:
    @pytest.mark.asyncio
    async def test_llm_provider_error(self) -> None:
        """LLM raises provider error — agent returns graceful message."""
        llm = _build_mock_llm([])
        llm.chat_with_tools = AsyncMock(side_effect=LLMProviderError("服务不可用"))
        agent = WanShiTongAgent(llm=llm, tools=_build_registry())

        result = await agent.chat("你好")

        assert "抱歉" in result
        assert "服务不可用" in result


class TestEmptyResponse:
    @pytest.mark.asyncio
    async def test_empty_response(self) -> None:
        """LLM returns empty content with no tool calls."""
        response = _make_response(content=None)
        llm = _build_mock_llm([response])
        agent = WanShiTongAgent(llm=llm, tools=_build_registry())

        result = await agent.chat("你好")

        assert result == ""
