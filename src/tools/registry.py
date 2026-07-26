"""ToolRegistry — central registry for tool schemas and executors."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel

from src.tools.base import pydantic_to_anthropic_tool, pydantic_to_openai_tool


class ToolExecutionError(Exception):
    def __init__(self, tool_name: str, message: str):
        self.tool_name = tool_name
        super().__init__(f"[{tool_name}] {message}")


@dataclass
class ToolEntry:
    name: str
    schema: type[BaseModel]
    description: str
    executor: Callable


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolEntry] = {}

    def register(
        self,
        name: str,
        schema: type[BaseModel],
        description: str,
        executor: Callable,
    ) -> None:
        self._tools[name] = ToolEntry(
            name=name, schema=schema, description=description, executor=executor
        )

    def get_openai_tools(self) -> list[dict[str, Any]]:
        return [
            pydantic_to_openai_tool(t.schema, t.name, t.description)
            for t in self._tools.values()
        ]

    def get_anthropic_tools(self) -> list[dict[str, Any]]:
        return [
            pydantic_to_anthropic_tool(t.schema, t.name, t.description)
            for t in self._tools.values()
        ]

    async def execute(self, name: str, arguments: dict[str, Any]) -> str:
        tool = self._tools.get(name)
        if not tool:
            return f"未知工具：{name}，可用工具：{list(self._tools.keys())}"
        params = tool.schema.model_validate(arguments)
        try:
            return await tool.executor(params)
        except Exception as e:
            raise ToolExecutionError(name, str(e))
