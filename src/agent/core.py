"""WanShiTongAgent — core conversation loop."""
from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from src.agent.config import AgentConfig
from src.llm.base import LLMProvider, LLMProviderError
from src.tools.registry import ToolExecutionError, ToolRegistry


class WanShiTongAgent:
    def __init__(
        self,
        llm: LLMProvider,
        tools: ToolRegistry,
        config: AgentConfig | None = None,
    ) -> None:
        self.llm = llm
        self.tools = tools
        self.config = config or AgentConfig()
        self.conversation_history: list[dict[str, Any]] = []

    async def chat(self, user_input: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_input})

        for _round in range(self.config.max_tool_rounds):
            try:
                response = await self.llm.chat_with_tools(
                    messages=self.conversation_history,
                    tools=self.tools.get_openai_tools(),
                )
            except LLMProviderError as e:
                return f"抱歉，AI 服务暂时不可用：{e}"

            if not response.tool_calls:
                self.conversation_history.append(
                    {"role": "assistant", "content": response.content}
                )
                return response.content or ""

            self.conversation_history.append(response.raw_message)

            for tool_call in response.tool_calls:
                try:
                    result = await self.tools.execute(
                        tool_call.name, tool_call.arguments
                    )
                except ValidationError as e:
                    result = f"参数校验错误：{e}"
                except ToolExecutionError as e:
                    result = f"工具调用失败：{e}"
                if not isinstance(result, str):
                    result = json.dumps(result, ensure_ascii=False)
                self.conversation_history.append(
                    self.llm.format_tool_result(tool_call.id, result)
                )

        return "抱歉，我尝试了很多次但没能完成这个任务，请换个方式描述一下？"
