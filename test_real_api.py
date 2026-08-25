"""Test script for real API tools."""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.tools.weather import weather_executor
from src.tools.search import search_executor
from src.tools.calendar import calendar_executor, reset_events
from src.tools.email_tool import email_executor, reset_inbox
from src.schema.types import WeatherParams, SearchParams, CalendarEventParams, EmailParams


async def test_weather():
    """测试天气工具"""
    print("=" * 50)
    print("测试天气工具 (Open-Meteo API)")
    print("=" * 50)
    params = WeatherParams(city="深圳龙岗")
    result = await weather_executor(params)
    print(f"结果:\n{result}\n")


async def test_search():
    """测试搜索工具"""
    print("=" * 50)
    print("测试搜索工具 (MiMo 内置搜索)")
    print("=" * 50)
    params = SearchParams(query="介绍一下雷军", num_results=3)
    result = await search_executor(params)
    print(f"结果:\n{result}\n")


async def test_calendar():
    """测试日历工具"""
    print("=" * 50)
    print("测试日历工具 (本地 JSON 存储)")
    print("=" * 50)

    # 重置数据
    reset_events()

    # 创建事件
    create_params = CalendarEventParams(
        action="create",
        title="团队周会",
        start_time="2026-08-15T10:00:00",
        end_time="2026-08-15T11:00:00"
    )
    result = await calendar_executor(create_params)
    print(f"创建事件: {result}")

    # 查询事件
    query_params = CalendarEventParams(action="query")
    result = await calendar_executor(query_params)
    print(f"查询结果:\n{result}\n")


async def test_email():
    """测试邮件工具"""
    print("=" * 50)
    print("测试邮件工具 (SMTP 发送)")
    print("=" * 50)

    # 重置数据
    reset_inbox()

    # 搜索邮件（测试本地存储）
    search_params = EmailParams(action="search", query="测试", limit=5)
    result = await email_executor(search_params)
    print(f"搜索邮件: {result}")

    # 读取邮件
    read_params = EmailParams(action="read", email_id="email_001")
    result = await email_executor(read_params)
    print(f"读取邮件: {result}\n")


async def test_all_tools():
    """测试所有工具"""
    print("开始测试真实 API 工具...\n")

    await test_weather()
    await test_search()
    await test_calendar()
    await test_email()

    print("=" * 50)
    print("所有测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_all_tools())