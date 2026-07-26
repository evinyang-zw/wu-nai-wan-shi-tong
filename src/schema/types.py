"""Tool parameter schema models for the personal assistant agent."""
from __future__ import annotations

from typing import Annotated, Literal, Optional

from pydantic import BaseModel, EmailStr, Field

# Type aliases for common constraints
PositiveInt = Annotated[int, Field(gt=0, description="Must be a positive integer")]
NonEmptyStr = Annotated[str, Field(min_length=1, description="Must not be empty")]


class CalendarEventParams(BaseModel):
    """Parameters for calendar event operations."""

    action: Literal["create", "query", "delete"] = Field(
        ..., description="The calendar action to perform"
    )
    title: Optional[str] = Field(None, description="Event title (required for create)")
    start_time: Optional[str] = Field(
        None, description="Event start time in ISO format (required for create)"
    )
    end_time: Optional[str] = Field(
        None, description="Event end time in ISO format (required for create)"
    )
    event_id: Optional[str] = Field(None, description="Event ID (required for delete)")
    date_range: Optional[str] = Field(
        None, description="Date range filter, e.g. '2024-01-01 to 2024-01-31' (for query)"
    )


class EmailParams(BaseModel):
    """Parameters for email operations."""

    action: Literal["send", "search", "read"] = Field(
        ..., description="The email action to perform"
    )
    to: Optional[EmailStr] = Field(None, description="Recipient email address (required for send)")
    subject: Optional[NonEmptyStr] = Field(None, description="Email subject (required for send)")
    body: Optional[str] = Field(None, description="Email body content")
    query: Optional[NonEmptyStr] = Field(
        None, description="Search query (required for search)"
    )
    email_id: Optional[str] = Field(None, description="Email ID (required for read)")
    limit: Optional[PositiveInt] = Field(
        None, description="Maximum number of results to return"
    )


class WeatherParams(BaseModel):
    """Parameters for weather queries."""

    city: NonEmptyStr = Field(..., description="City name to get weather for")
    include_forecast: bool = Field(False, description="Whether to include forecast data")
    forecast_days: Annotated[int, Field(ge=1, le=7)] = Field(
        3, description="Number of forecast days (1-7)"
    )


class SearchParams(BaseModel):
    """Parameters for web search operations."""

    query: NonEmptyStr = Field(..., description="Search query string")
    num_results: PositiveInt = Field(5, description="Number of results to return")
