"""Weather tool executor."""
from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any

from src.schema.types import WeatherParams

# Weather conditions for mock data
WEATHER_CONDITIONS = ["晴", "多云", "阴", "小雨", "大雨", "雪", "雾"]


async def weather_executor(params: WeatherParams) -> Any:
    """Execute weather queries.
    
    Args:
        params: Weather query parameters
        
    Returns:
        Weather data
    """
    # Generate current weather
    current_weather = {
        "city": params.city,
        "temperature": random.randint(5, 35),
        "condition": random.choice(WEATHER_CONDITIONS),
        "humidity": random.randint(30, 80),
        "timestamp": datetime.now().isoformat(),
    }
    
    # Add forecast if requested
    if params.include_forecast:
        forecast = []
        today = datetime.now().date()
        for i in range(params.forecast_days):
            forecast_date = today + timedelta(days=i + 1)
            forecast.append({
                "date": forecast_date.isoformat(),
                "temperature": random.randint(5, 35),
                "condition": random.choice(WEATHER_CONDITIONS),
            })
        current_weather["forecast"] = forecast
    
    return current_weather