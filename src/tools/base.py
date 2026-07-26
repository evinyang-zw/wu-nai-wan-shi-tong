"""Schema → LLM format conversion functions."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


def pydantic_to_openai_tool(
    schema_model: type[BaseModel], name: str, description: str
) -> dict[str, Any]:
    """Convert a Pydantic model to OpenAI function calling format.

    Args:
        schema_model: The Pydantic model class
        name: Tool name
        description: Tool description

    Returns:
        OpenAI function calling format dict
    """
    json_schema = schema_model.model_json_schema()
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": json_schema.get("properties", {}),
                "required": json_schema.get("required", []),
            },
        },
    }


def pydantic_to_anthropic_tool(
    schema_model: type[BaseModel], name: str, description: str
) -> dict[str, Any]:
    """Convert a Pydantic model to Anthropic tool use format.

    Args:
        schema_model: The Pydantic model class
        name: Tool name
        description: Tool description

    Returns:
        Anthropic tool use format dict
    """
    json_schema = schema_model.model_json_schema()
    return {
        "name": name,
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": json_schema.get("properties", {}),
            "required": json_schema.get("required", []),
        },
    }
