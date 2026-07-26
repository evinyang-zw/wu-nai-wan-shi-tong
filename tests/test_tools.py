"""Tests for tool executor functions."""
import pytest
from src.tools.calendar import calendar_executor
from src.tools.email_tool import email_executor
from src.tools.weather import weather_executor
from src.tools.search import search_executor
from src.schema.types import CalendarEventParams, EmailParams, WeatherParams, SearchParams


class TestCalendarTool:
    """Tests for calendar executor."""

    @pytest.mark.asyncio
    async def test_create_event(self):
        """Test creating a calendar event."""
        params = CalendarEventParams(
            action="create",
            title="Team Meeting",
            start_time="2024-01-15T10:00:00",
            end_time="2024-01-15T11:00:00",
        )
        result = await calendar_executor(params)
        assert "event_id" in result
        assert result["title"] == "Team Meeting"
        assert result["start_time"] == "2024-01-15T10:00:00"
        assert result["end_time"] == "2024-01-15T11:00:00"
        assert result["created_at"] is not None

    @pytest.mark.asyncio
    async def test_query_events(self):
        """Test querying calendar events."""
        # First create an event
        create_params = CalendarEventParams(
            action="create",
            title="Test Event",
            start_time="2024-01-15T10:00:00",
            end_time="2024-01-15T11:00:00",
        )
        created = await calendar_executor(create_params)
        
        # Query events
        query_params = CalendarEventParams(
            action="query",
            date_range="2024-01-01 to 2024-01-31",
        )
        result = await calendar_executor(query_params)
        assert isinstance(result, list)
        assert len(result) >= 1
        # Find the event we just created
        found = any(event["event_id"] == created["event_id"] for event in result)
        assert found, "Created event not found in query results"

    @pytest.mark.asyncio
    async def test_delete_event(self):
        """Test deleting a calendar event."""
        # Create an event first
        create_params = CalendarEventParams(
            action="create",
            title="To Delete",
            start_time="2024-01-15T10:00:00",
            end_time="2024-01-15T11:00:00",
        )
        created = await calendar_executor(create_params)
        event_id = created["event_id"]
        
        # Delete the event
        delete_params = CalendarEventParams(
            action="delete",
            event_id=event_id,
        )
        result = await calendar_executor(delete_params)
        assert result["deleted"] is True
        assert result["event_id"] == event_id


class TestEmailTool:
    """Tests for email executor."""

    @pytest.mark.asyncio
    async def test_send_email(self):
        """Test sending an email."""
        params = EmailParams(
            action="send",
            to="user@example.com",
            subject="Test Email",
            body="This is a test email.",
        )
        result = await email_executor(params)
        assert result["sent"] is True
        assert result["to"] == "user@example.com"
        assert result["subject"] == "Test Email"

    @pytest.mark.asyncio
    async def test_search_emails(self):
        """Test searching emails."""
        params = EmailParams(
            action="search",
            query="meeting",
            limit=5,
        )
        result = await email_executor(params)
        assert isinstance(result, list)
        assert len(result) <= 5
        # Should find the boss meeting reminder in sample data
        assert any("meeting" in email["subject"].lower() for email in result)


class TestWeatherTool:
    """Tests for weather executor."""

    @pytest.mark.asyncio
    async def test_basic_weather(self):
        """Test basic weather query."""
        params = WeatherParams(city="Beijing")
        result = await weather_executor(params)
        assert result["city"] == "Beijing"
        assert "temperature" in result
        assert "condition" in result
        assert "humidity" in result
        assert isinstance(result["temperature"], int)
        assert 5 <= result["temperature"] <= 35
        assert isinstance(result["humidity"], int)
        assert 30 <= result["humidity"] <= 80

    @pytest.mark.asyncio
    async def test_weather_with_forecast(self):
        """Test weather query with forecast."""
        params = WeatherParams(
            city="Shanghai",
            include_forecast=True,
            forecast_days=3,
        )
        result = await weather_executor(params)
        assert result["city"] == "Shanghai"
        assert "forecast" in result
        assert len(result["forecast"]) == 3
        for day in result["forecast"]:
            assert "date" in day
            assert "temperature" in day
            assert "condition" in day


class TestSearchTool:
    """Tests for search executor."""

    @pytest.mark.asyncio
    async def test_basic_search(self):
        """Test basic search."""
        params = SearchParams(query="Python tutorial")
        result = await search_executor(params)
        assert isinstance(result, str)
        assert "Python tutorial" in result
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_search_with_limit(self):
        """Test search with custom limit."""
        params = SearchParams(query="machine learning", num_results=3)
        result = await search_executor(params)
        assert isinstance(result, str)
        assert "machine learning" in result