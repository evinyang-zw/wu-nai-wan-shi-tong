"""Search tool executor using MiMo built-in web search."""
from __future__ import annotations

import os
import json
from openai import AsyncOpenAI
from src.schema.types import SearchParams


async def search_executor(params: SearchParams) -> str:
    """Execute web search queries using MiMo built-in web search.

    Args:
        params: Search query parameters

    Returns:
        Formatted search results string
    """
    # Get LLM configuration
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("LLM_BASE_URL", "https://api.xiaomimimo.com/v1")
    model = os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL", "MiMo-V2.5")

    if not api_key:
        return "搜索失败：未配置 LLM API Key。请在 .env 文件中设置 LLM_API_KEY 或 OPENAI_API_KEY。"

    try:
        client = AsyncOpenAI(api_key=api_key, base_url=base_url)

        # Define web_search tool for MiMo
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "搜索互联网获取最新信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索查询关键词"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

        # First call: let MiMo decide to use web_search
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": f"你是一个有用的助手。请搜索以下内容并返回{params.num_results}条最相关的结果：{params.query}"
                },
                {
                    "role": "user",
                    "content": f"请搜索：{params.query}"
                }
            ],
            tools=tools,
            tool_choice="auto",
        )

        message = response.choices[0].message

        # If MiMo wants to call web_search, execute it
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            tool_args = json.loads(tool_call.function.arguments)

            # MiMo handles the search internally, we just need to continue the conversation
            # Add the tool call and result to messages
            messages = [
                {
                    "role": "system",
                    "content": f"你是一个有用的助手。请搜索以下内容并返回{params.num_results}条最相关的结果：{params.query}"
                },
                {
                    "role": "user",
                    "content": f"请搜索：{params.query}"
                },
                message,
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": "搜索完成，请根据搜索结果回答用户的问题。"
                }
            ]

            # Second call: get final answer with search results
            final_response = await client.chat.completions.create(
                model=model,
                messages=messages,
            )

            return final_response.choices[0].message.content

        # If MiMo didn't use web_search, return direct response
        return message.content or "搜索未返回结果。"

    except Exception as e:
        return f"搜索失败: {str(e)}"