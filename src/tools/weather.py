"""Weather tool executor using Open-Meteo API."""
from __future__ import annotations

import httpx
from src.schema.types import WeatherParams

# WMO weather code to Chinese description mapping
WMO_CODES = {
    0: "晴",
    1: "大部晴朗",
    2: "局部多云",
    3: "多云",
    45: "雾",
    48: "雾凇",
    51: "小毛毛雨",
    53: "中毛毛雨",
    55: "大毛毛雨",
    56: "冻毛毛雨",
    57: "冻毛毛雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    66: "冻雨",
    67: "冻雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    77: "雪粒",
    80: "小阵雨",
    81: "中阵雨",
    82: "大阵雨",
    85: "小阵雪",
    86: "大阵雪",
    95: "雷暴",
    96: "雷暴伴小冰雹",
    99: "雷暴伴大冰雹",
}

# Common city coordinates (fallback if geocoding fails)
CITY_COORDS = {
    "北京": (39.9042, 116.4074),
    "上海": (31.2304, 121.4737),
    "广州": (23.1291, 113.2644),
    "深圳": (22.5431, 114.0579),
    "杭州": (30.2741, 120.1551),
    "成都": (30.5728, 104.0668),
    "武汉": (30.5928, 114.3055),
    "西安": (34.3416, 108.9398),
    "南京": (32.0603, 118.7969),
    "重庆": (29.4316, 106.9123),
}


async def _get_coordinates(city: str) -> tuple[float, float] | None:
    """Get city coordinates via Open-Meteo Geocoding API."""
    # Check local cache first
    for name, coords in CITY_COORDS.items():
        if name in city:
            return coords

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1, "language": "zh"},
            )
            data = resp.json()
            if "results" in data and data["results"]:
                result = data["results"][0]
                return (result["latitude"], result["longitude"])
    except Exception:
        pass

    return None


def _get_weather_description(code: int) -> str:
    """Convert WMO weather code to Chinese description."""
    return WMO_CODES.get(code, f"未知({code})")


async def weather_executor(params: WeatherParams) -> str:
    """Execute weather queries using Open-Meteo API.

    Args:
        params: Weather query parameters

    Returns:
        Human-readable weather report string
    """
    # Get coordinates
    coords = await _get_coordinates(params.city)
    if not coords:
        return f"无法获取 '{params.city}' 的坐标信息，请检查城市名称。"

    lat, lon = coords

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Build request parameters
            request_params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                "timezone": "Asia/Shanghai",
            }

            # Add forecast if requested
            if params.include_forecast:
                request_params["daily"] = "weather_code,temperature_2m_max,temperature_2m_min"
                request_params["forecast_days"] = params.forecast_days

            resp = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params=request_params,
            )
            data = resp.json()

            if "error" in data:
                return f"天气 API 错误: {data['reason']}"

            # Parse current weather
            current = data.get("current", {})
            temp = current.get("temperature_2m", "N/A")
            humidity = current.get("relative_humidity_2m", "N/A")
            weather_code = current.get("weather_code", -1)
            wind_speed = current.get("wind_speed_10m", "N/A")

            weather_desc = _get_weather_description(weather_code)

            lines = [
                f"{params.city} 当前天气：",
                f"  温度: {temp}°C",
                f"  天气: {weather_desc}",
                f"  湿度: {humidity}%",
                f"  风速: {wind_speed} km/h",
            ]

            # Add forecast if requested
            if params.include_forecast and "daily" in data:
                daily = data["daily"]
                dates = daily.get("time", [])
                max_temps = daily.get("temperature_2m_max", [])
                min_temps = daily.get("temperature_2m_min", [])
                daily_codes = daily.get("weather_code", [])

                lines.append(f"\n未来 {params.forecast_days} 天预报：")
                for i in range(min(len(dates), params.forecast_days)):
                    date = dates[i]
                    max_temp = max_temps[i] if i < len(max_temps) else "N/A"
                    min_temp = min_temps[i] if i < len(min_temps) else "N/A"
                    day_code = daily_codes[i] if i < len(daily_codes) else -1
                    day_desc = _get_weather_description(day_code)
                    lines.append(f"  {date}: {day_desc}, {min_temp}°C ~ {max_temp}°C")

            return "\n".join(lines)

    except httpx.TimeoutException:
        return "天气 API 请求超时，请稍后重试。"
    except Exception as e:
        return f"获取天气信息失败: {str(e)}"