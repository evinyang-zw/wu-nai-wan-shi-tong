from __future__ import annotations

import json
from typing import Any

from anthropic import AsyncAnthropic

from src.llm.base import LLMProvider, LLMProviderError, LLMResponse, ToolCall


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514") -> None:
        self._client = AsyncAnthropic(api_key=api_key)
        self._model = model

    async def chat_with_tools(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]
    ) -> LLMResponse:
        system_msg = ""
        anthropic_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_msg = msg.get("content", "")
            else:
                anthropic_messages.append(msg)

        try:
            kwargs: dict[str, Any] = {
                "model": self._model,
                "max_tokens": 4096,
                "messages": anthropic_messages,
            }
            if system_msg:
                kwargs["system"] = system_msg
            if tools:
                kwargs["tools"] = tools
            response = await self._client.messages.create(**kwargs)
        except Exception as e:
            raise LLMProviderError(f"Anthropic API 调用失败: {e}") from e

        tool_calls = None
        text_content = ""
        for block in response.content:
            if block.type == "text":
                text_content += block.text
            elif block.type == "tool_use":
                if tool_calls is None:
                    tool_calls = []
                tool_calls.append(
                    ToolCall(id=block.id, name=block.name, arguments=block.input)
                )

        raw_message = {"role": "assistant", "content": response.content}
        return LLMResponse(
            content=text_content if text_content else None,
            tool_calls=tool_calls,
            raw_message=raw_message,
        )

    def format_tool_result(self, tool_call_id: str, result: str) -> dict[str, Any]:
        return {
            "role": "user",
            "content": [{"type": "tool_result", "tool_use_id": tool_call_id, "content": result}],
        }
