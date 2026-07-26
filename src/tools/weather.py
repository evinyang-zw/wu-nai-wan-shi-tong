"""Weather tool executor."""
from __future__ import annotations

import random

from src.schema.types import WeatherParams

# Weather conditions for mock data
WEATHER_CONDITIONS = ["晴", "多云", "阴", "小雨", "大雨", "雪", "雾"]


async def weather_executor(params: WeatherParams) -> str:
    """Execute weather queries.

    Args:
        params: Weather query parameters

    Returns:
        Human-readable weather report string
    """
    temp = random.randint(5, 35)
    condition = random.choice(WEATHER_CONDITIONS)
    humidity = random.randint(30, 80)

    lines = [
        f"{params.city} 当前天气：",
        f"  温度: {temp}°C",
        f"  天气: {condition}",
        f"  湿度: {humidity}%",
    ]

    if params.include_forecast:
        lines.append(f"\n未来 {params.forecast_days} 天预报：")
        for i in range(params.forecast_days):
            f_temp = random.randint(3, 33)
            f_condition = random.choice(WEATHER_CONDITIONS)
            lines.append(f"  第 {i + 1} 天: {f_condition}, {f_temp}°C")

    return "\n".join(lines)
