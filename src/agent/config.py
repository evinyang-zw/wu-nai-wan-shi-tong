from __future__ import annotations
import os
from dataclasses import dataclass


@dataclass
class AgentConfig:
    provider: str = "openai"
    api_key: str = ""
    model: str = ""
    max_tool_rounds: int = 10

    @classmethod
    def from_env(cls) -> AgentConfig:
        provider = os.getenv("LLM_PROVIDER", "openai")
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY", "")
            model = os.getenv("OPENAI_MODEL", "gpt-4o")
        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
            model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        else:
            api_key = ""
            model = ""
        return cls(provider=provider, api_key=api_key, model=model)
