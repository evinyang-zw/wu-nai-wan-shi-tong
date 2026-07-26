"""Tests for tool parameter schema models."""
import pytest
from pydantic import ValidationError
from src.schema.types import (
    CalendarEventParams,
    EmailParams,
    WeatherParams,
    SearchParams,
    PositiveInt,
    NonEmptyStr,
)


class TestCalendarEventParams:
    """Tests for CalendarEventParams schema."""

    def test_create_action(self):
        """Test creating a calendar event with 'create' action."""
        params = CalendarEventParams(
            action="create",
            title="Team Meeting",
            start_time="2024-01-15T10:00:00",
            end_time="2024-01-15T11:00:00",
        )
        assert params.action == "create"
        assert params.title == "Team Meeting"

    def test_query_action(self):
        """Test querying calendar events with 'query' action."""
        params = CalendarEventParams(
            action="query",
            date_range="2024-01-01 to 2024-01-31",
        )
        assert params.action == "query"
        assert params.date_range == "2024-01-01 to 2024-01-31"

    def test_delete_action(self):
        """Test deleting a calendar event with 'delete' action."""
        params = CalendarEventParams(
            action="delete",
            event_id="evt_12345",
        )
        assert params.action == "delete"
        assert params.event_id == "evt_12345"

    def test_invalid_action(self):
        """Test that invalid action raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            CalendarEventParams(action="invalid_action")
        assert "action" in str(exc_info.value)

    def test_from_llm_dict(self):
        """Test creating CalendarEventParams from a dictionary (LLM output)."""
        llm_output = {
            "action": "create",
            "title": "Birthday Party",
            "start_time": "2024-03-20T18:00:00",
            "end_time": "2024-03-20T21:00:00",
        }
        params = CalendarEventParams(**llm_output)
        assert params.action == "create"
        assert params.title == "Birthday Party"


class TestEmailParams:
    """Tests for EmailParams schema."""

    def test_send_action(self):
        """Test sending an email with 'send' action."""
        params = EmailParams(
            action="send",
            to="user@example.com",
            subject="Hello",
            body="This is a test email.",
        )
        assert params.action == "send"
        assert params.to == "user@example.com"

    def test_search_action(self):
        """Test searching emails with 'search' action."""
        params = EmailParams(
            action="search",
            query="meeting tomorrow",
            limit=10,
        )
        assert params.action == "search"
        assert params.query == "meeting tomorrow"

    def test_invalid_action(self):
        """Test that invalid action raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            EmailParams(action="delete")
        assert "action" in str(exc_info.value)

    def test_invalid_email_format(self):
        """Test that invalid email format raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            EmailParams(
                action="send",
                to="not-an-email",
                subject="Test",
                body="Hello",
            )
        assert "to" in str(exc_info.value)


class TestWeatherParams:
    """Tests for WeatherParams schema."""

    def test_basic_query(self):
        """Test basic weather query with city only."""
        params = WeatherParams(city="Beijing")
        assert params.city == "Beijing"
        assert params.include_forecast is False

    def test_with_forecast(self):
        """Test weather query with forecast enabled."""
        params = WeatherParams(
            city="Shanghai",
            include_forecast=True,
            forecast_days=5,
        )
        assert params.include_forecast is True
        assert params.forecast_days == 5

    def test_empty_city(self):
        """Test that empty city raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            WeatherParams(city="")
        assert "city" in str(exc_info.value)

    def test_forecast_days_range(self):
        """Test that forecast_days must be between 1 and 7."""
        # Valid: 1
        params = WeatherParams(city="Tokyo", forecast_days=1)
        assert params.forecast_days == 1

        # Valid: 7
        params = WeatherParams(city="Tokyo", forecast_days=7)
        assert params.forecast_days == 7

        # Invalid: 0
        with pytest.raises(ValidationError):
            WeatherParams(city="Tokyo", forecast_days=0)

        # Invalid: 8
        with pytest.raises(ValidationError):
            WeatherParams(city="Tokyo", forecast_days=8)


class TestSearchParams:
    """Tests for SearchParams schema."""

    def test_basic_search(self):
        """Test basic search with query only."""
        params = SearchParams(query="Python tutorial")
        assert params.query == "Python tutorial"
        assert params.num_results == 5  # default

    def test_custom_results(self):
        """Test search with custom num_results."""
        params = SearchParams(query="machine learning", num_results=20)
        assert params.num_results == 20

    def test_empty_query(self):
        """Test that empty query raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SearchParams(query="")
        assert "query" in str(exc_info.value)


class TestTypeAliases:
    """Tests for type aliases (PositiveInt, NonEmptyStr)."""

    def test_positive_int(self):
        """Test PositiveInt type alias."""
        # Valid
        value: PositiveInt = 5
        assert value > 0

        # Invalid via schema
        with pytest.raises(ValidationError):
            SearchParams(query="test", num_results=-1)

    def test_non_empty_str(self):
        """Test NonEmptyStr type alias."""
        # Valid
        value: NonEmptyStr = "hello"
        assert len(value) > 0
