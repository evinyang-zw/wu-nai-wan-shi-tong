"""Tests for tool executor functions."""
import pytest
from src.tools.calendar import calendar_executor, reset_events
from src.tools.email_tool import email_executor, reset_inbox
from src.tools.weather import weather_executor
from src.tools.search import search_executor
from src.schema.types import CalendarEventParams, EmailParams, WeatherParams, SearchParams


class TestCalendarTool:
    """Tests for calendar executor."""

    def setup_method(self):
        reset_events()

    @pytest.mark.asyncio
    async def test_create_event(self):
        """Test creating a calendar event."""
        params = CalendarEventParams(
            action="create",
            title="团队会议",
            start_time="2024-01-15T10:00:00",
            end_time="2024-01-15T11:00:00",
        )
        result = await calendar_executor(params)
        assert isinstance(result, str)
        assert "evt_" in result
        assert "团队会议" in result

    @pytest.mark.asyncio
    async def test_query_events(self):
        """Test querying calendar events."""
        # Create an event first
        create_params = CalendarEventParams(
            action="create",
            title="测试事件",
            start_time="2024-01-15T10:00:00",
            end_time="2024-01-15T11:00:00",
        )
        await calendar_executor(create_params)

        # Query events
        query_params = CalendarEventParams(action="query")
        result = await calendar_executor(query_params)
        assert isinstance(result, str)
        assert "测试事件" in result

    @pytest.mark.asyncio
    async def test_query_empty(self):
        """Test querying with no events."""
        query_params = CalendarEventParams(action="query")
        result = await calendar_executor(query_params)
        assert isinstance(result, str)
        assert "没有日程" in result

    @pytest.mark.asyncio
    async def test_delete_event(self):
        """Test deleting a calendar event."""
        # Create an event first
        create_params = CalendarEventParams(
            action="create",
            title="待删除",
            start_time="2024-01-15T10:00:00",
            end_time="2024-01-15T11:00:00",
        )
        create_result = await calendar_executor(create_params)
        # Extract event_id from result string
        import re
        match = re.search(r"evt_\w+", create_result)
        assert match, "创建结果应包含 event_id"
        event_id = match.group(0)

        # Delete the event
        delete_params = CalendarEventParams(action="delete", event_id=event_id)
        result = await calendar_executor(delete_params)
        assert isinstance(result, str)
        assert "已删除" in result

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self):
        """Test deleting a nonexistent event."""
        delete_params = CalendarEventParams(action="delete", event_id="evt_nonexistent")
        result = await calendar_executor(delete_params)
        assert isinstance(result, str)
        assert "未找到" in result


class TestEmailTool:
    """Tests for email executor."""

    def setup_method(self):
        reset_inbox()

    @pytest.mark.asyncio
    async def test_send_email(self):
        """Test sending an email."""
        params = EmailParams(
            action="send",
            to="user@example.com",
            subject="测试邮件",
            body="这是一封测试邮件。",
        )
        result = await email_executor(params)
        assert isinstance(result, str)
        assert "发送成功" in result
        assert "user@example.com" in result

    @pytest.mark.asyncio
    async def test_search_emails(self):
        """Test searching emails."""
        params = EmailParams(
            action="search",
            query="会议",
            limit=5,
        )
        result = await email_executor(params)
        assert isinstance(result, str)
        assert "会议" in result

    @pytest.mark.asyncio
    async def test_read_email(self):
        """Test reading a specific email."""
        params = EmailParams(action="read", email_id="email_001")
        result = await email_executor(params)
        assert isinstance(result, str)
        assert "boss@company.com" in result

    @pytest.mark.asyncio
    async def test_read_nonexistent(self):
        """Test reading a nonexistent email."""
        params = EmailParams(action="read", email_id="email_999")
        result = await email_executor(params)
        assert isinstance(result, str)
        assert "未找到" in result


class TestWeatherTool:
    """Tests for weather executor."""

    @pytest.mark.asyncio
    async def test_basic_weather(self):
        """Test basic weather query."""
        params = WeatherParams(city="北京")
        result = await weather_executor(params)
        assert isinstance(result, str)
        assert "北京" in result
        assert "°C" in result

    @pytest.mark.asyncio
    async def test_weather_with_forecast(self):
        """Test weather query with forecast."""
        params = WeatherParams(
            city="上海",
            include_forecast=True,
            forecast_days=3,
        )
        result = await weather_executor(params)
        assert isinstance(result, str)
        assert "上海" in result
        assert "预报" in result


class TestSearchTool:
    """Tests for search executor."""

    @pytest.mark.asyncio
    async def test_basic_search(self):
        """Test basic search."""
        params = SearchParams(query="Python tutorial")
        result = await search_executor(params)
        assert isinstance(result, str)
        assert "Python tutorial" in result

    @pytest.mark.asyncio
    async def test_search_with_limit(self):
        """Test search with custom limit."""
        params = SearchParams(query="machine learning", num_results=3)
        result = await search_executor(params)
        assert isinstance(result, str)
        assert "machine learning" in result
