from __future__ import annotations

import json
from typing import Any

from openai import AsyncOpenAI

from src.llm.base import LLMProvider, LLMProviderError, LLMResponse, ToolCall


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o") -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def chat_with_tools(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]
    ) -> LLMResponse:
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                tools=tools if tools else None,
            )
        except Exception as e:
            raise LLMProviderError(f"OpenAI API 调用失败: {e}") from e

        message = response.choices[0].message
        tool_calls = None
        if message.tool_calls:
            tool_calls = [
                ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments),
                )
                for tc in message.tool_calls
            ]

        raw_message: dict[str, Any] = {"role": "assistant", "content": message.content}
        if message.tool_calls:
            raw_message["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ]

        return LLMResponse(
            content=message.content, tool_calls=tool_calls, raw_message=raw_message
        )

    def format_tool_result(self, tool_call_id: str, result: str) -> dict[str, Any]:
        return {"role": "tool", "tool_call_id": tool_call_id, "content": result}
