"""Tests for Schema → LLM format conversion functions."""
from __future__ import annotations

from typing import Literal, Optional

import pytest
from pydantic import BaseModel, Field

from src.tools.base import pydantic_to_anthropic_tool, pydantic_to_openai_tool


class SampleModel(BaseModel):
    """A simple model for testing."""

    name: str = Field(..., description="The name")
    count: int = Field(5, description="Number of items")


class OptionalModel(BaseModel):
    """Model with optional fields."""

    required_field: str = Field(..., description="This is required")
    optional_field: Optional[str] = Field(None, description="This is optional")


class CalendarModel(BaseModel):
    """Calendar event parameters."""

    action: Literal["create", "query", "delete"] = Field(
        ..., description="The calendar action"
    )
    title: Optional[str] = Field(None, description="Event title")
    event_id: Optional[str] = Field(None, description="Event ID")


class TestOpenAIFormat:
    """Tests for OpenAI function calling format."""

    def test_basic_conversion(self):
        result = pydantic_to_openai_tool(SampleModel, "get_sample", "Get a sample")

        assert result["type"] == "function"
        assert result["function"]["name"] == "get_sample"
        assert result["function"]["description"] == "Get a sample"
        assert "parameters" in result["function"]
        assert result["function"]["parameters"]["type"] == "object"
        assert "name" in result["function"]["parameters"]["properties"]
        assert "count" in result["function"]["parameters"]["properties"]
        assert result["function"]["parameters"]["required"] == ["name"]

    def test_optional_fields_not_required(self):
        result = pydantic_to_openai_tool(
            OptionalModel, "optional_test", "Test optional fields"
        )

        assert result["function"]["parameters"]["required"] == ["required_field"]
        assert "optional_field" in result["function"]["parameters"]["properties"]

    def test_calendar_tool(self):
        result = pydantic_to_openai_tool(
            CalendarModel, "calendar_event", "Manage calendar events"
        )

        assert result["type"] == "function"
        assert result["function"]["name"] == "calendar_event"
        assert result["function"]["description"] == "Manage calendar events"
        assert result["function"]["parameters"]["required"] == ["action"]
        assert "title" in result["function"]["parameters"]["properties"]
        assert "event_id" in result["function"]["parameters"]["properties"]


class TestAnthropicFormat:
    """Tests for Anthropic tool use format."""

    def test_basic_conversion(self):
        result = pydantic_to_anthropic_tool(SampleModel, "get_sample", "Get a sample")

        assert result["name"] == "get_sample"
        assert result["description"] == "Get a sample"
        assert "input_schema" in result
        assert result["input_schema"]["type"] == "object"
        assert "name" in result["input_schema"]["properties"]
        assert "count" in result["input_schema"]["properties"]
        assert result["input_schema"]["required"] == ["name"]

    def test_required_fields(self):
        result = pydantic_to_anthropic_tool(
            CalendarModel, "calendar_event", "Manage calendar events"
        )

        assert result["name"] == "calendar_event"
        assert result["input_schema"]["required"] == ["action"]
        assert "title" in result["input_schema"]["properties"]
        assert "event_id" in result["input_schema"]["properties"]
