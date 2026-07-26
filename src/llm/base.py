from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    content: str | None
    tool_calls: list[ToolCall] | None
    raw_message: dict[str, Any]


class LLMProviderError(Exception):
    pass


class LLMProvider(ABC):
    @abstractmethod
    async def chat_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> LLMResponse:
        ...

    @abstractmethod
    def format_tool_result(self, tool_call_id: str, result: str) -> dict[str, Any]:
        ...
