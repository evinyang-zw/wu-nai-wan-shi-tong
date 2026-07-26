"""Tests for ToolRegistry."""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest
from pydantic import BaseModel, ValidationError

from src.tools.registry import ToolExecutionError, ToolRegistry


class EchoSchema(BaseModel):
    message: str


class AddSchema(BaseModel):
    a: int
    b: int


async def echo_executor(params: EchoSchema) -> str:
    return params.message


async def add_executor(params: AddSchema) -> str:
    return str(params.a + params.b)


async def failing_executor(params: EchoSchema) -> str:
    raise RuntimeError("boom")


class TestRegisterAndGetTools:
    def test_register_and_get_tools(self) -> None:
        registry = ToolRegistry()
        registry.register("echo", EchoSchema, "Echo back", echo_executor)
        tools = registry.get_openai_tools()
        assert len(tools) == 1
        assert tools[0]["function"]["name"] == "echo"

    def test_register_multiple_tools(self) -> None:
        registry = ToolRegistry()
        registry.register("echo", EchoSchema, "Echo back", echo_executor)
        registry.register("add", AddSchema, "Add two numbers", add_executor)
        tools = registry.get_openai_tools()
        names = {t["function"]["name"] for t in tools}
        assert names == {"echo", "add"}

    def test_anthropic_format(self) -> None:
        registry = ToolRegistry()
        registry.register("echo", EchoSchema, "Echo back", echo_executor)
        tools = registry.get_anthropic_tools()
        assert len(tools) == 1
        assert tools[0]["name"] == "echo"
        assert "input_schema" in tools[0]


class TestExecute:
    @pytest.mark.asyncio
    async def test_execute_tool(self) -> None:
        registry = ToolRegistry()
        registry.register("echo", EchoSchema, "Echo back", echo_executor)
        result = await registry.execute("echo", {"message": "hello"})
        assert result == "hello"

    @pytest.mark.asyncio
    async def test_execute_unknown_tool(self) -> None:
        registry = ToolRegistry()
        result = await registry.execute("nonexistent", {})
        assert "未知工具" in result

    @pytest.mark.asyncio
    async def test_execute_with_invalid_params(self) -> None:
        registry = ToolRegistry()
        registry.register("add", AddSchema, "Add two numbers", add_executor)
        with pytest.raises(ValidationError):
            await registry.execute("add", {"a": "not_a_number", "b": 1})

    @pytest.mark.asyncio
    async def test_execute_executor_error(self) -> None:
        registry = ToolRegistry()
        registry.register("fail", EchoSchema, "Always fails", failing_executor)
        with pytest.raises(ToolExecutionError) as exc_info:
            await registry.execute("fail", {"message": "hi"})
        assert exc_info.value.tool_name == "fail"
        assert "boom" in str(exc_info.value)
