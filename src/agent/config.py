from __future__ import annotations
import os
from dataclasses import dataclass


@dataclass
class AgentConfig:
    provider: str = "openai"
    api_key: str = ""
    model: str = ""
    base_url: str = ""
    max_tool_rounds: int = 10

    # SMTP configuration
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""

    # Calendar data directory
    calendar_data_dir: str = "~/.wanshitong"

    @classmethod
    def from_env(cls) -> AgentConfig:
        provider = os.getenv("LLM_PROVIDER", "openai")
        base_url = os.getenv("LLM_BASE_URL", "")
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY", "")
            model = os.getenv("OPENAI_MODEL", "gpt-4o")
        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
            model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        else:
            api_key = os.getenv("LLM_API_KEY", "")
            model = os.getenv("LLM_MODEL", "")

        # SMTP configuration
        smtp_host = os.getenv("SMTP_HOST", "smtp.qq.com")
        smtp_port = int(os.getenv("SMTP_PORT", "465"))
        smtp_user = os.getenv("SMTP_USER", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        smtp_from = os.getenv("SMTP_FROM", smtp_user)

        # Calendar data directory
        calendar_data_dir = os.getenv("CALENDAR_DATA_DIR", "~/.wanshitong")

        return cls(
            provider=provider,
            api_key=api_key,
            model=model,
            base_url=base_url,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            smtp_from=smtp_from,
            calendar_data_dir=calendar_data_dir,
        )