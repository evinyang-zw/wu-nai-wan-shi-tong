# src/main.py
"""吾乃万事通 — CLI 入口，交互式对话"""
from __future__ import annotations
import asyncio
import sys
from dotenv import load_dotenv
from src.agent.config import AgentConfig
from src.agent.core import WanShiTongAgent
from src.llm.factory import create_llm_provider
from src.schema.types import CalendarEventParams, EmailParams, SearchParams, WeatherParams
from src.tools.calendar import calendar_executor
from src.tools.email_tool import email_executor
from src.tools.registry import ToolRegistry
from src.tools.search import search_executor
from src.tools.weather import weather_executor

def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register("calendar", CalendarEventParams, "管理日历事件：创建、查询、删除日程安排", calendar_executor)
    registry.register("send_email", EmailParams, "发送邮件、查看收件箱、搜索邮件", email_executor)
    registry.register("get_weather", WeatherParams, "查询指定城市的当前天气和未来预报", weather_executor)
    registry.register("web_search", SearchParams, "搜索互联网获取实时信息", search_executor)
    return registry

async def main() -> None:
    load_dotenv()
    config = AgentConfig.from_env()
    if not config.api_key:
        print("错误：请设置 LLM API Key 环境变量")
        print("参考 .env.example 配置")
        sys.exit(1)
    llm = create_llm_provider(config.provider, api_key=config.api_key, model=config.model, base_url=config.base_url)
    tools = build_registry()
    agent = WanShiTongAgent(llm=llm, tools=tools, config=config)
    print(f"吾乃万事通 — 个人助手 (LLM: {config.provider}/{config.model})")
    print("输入 'quit' 或 'exit' 退出\n")
    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "退出"):
            print("再见！")
            break
        response = await agent.chat(user_input)
        print(f"万事通: {response}\n")

if __name__ == "__main__":
    asyncio.run(main())
