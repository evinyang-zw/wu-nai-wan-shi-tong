"""Tests for AgentConfig dataclass."""
import os
import pytest
from unittest.mock import patch
from src.agent.config import AgentConfig


class TestAgentConfigDefaults:
    """Tests for default configuration values."""

    def test_default_config(self):
        """Test that AgentConfig has correct defaults."""
        config = AgentConfig()
        assert config.provider == "openai"
        assert config.api_key == ""
        assert config.model == ""
        assert config.max_tool_rounds == 10


class TestAgentConfigCustom:
    """Tests for custom configuration values."""

    def test_custom_config(self):
        """Test creating AgentConfig with custom values."""
        config = AgentConfig(
            provider="anthropic",
            api_key="sk-test-key",
            model="claude-sonnet-4-20250514",
            max_tool_rounds=5,
        )
        assert config.provider == "anthropic"
        assert config.api_key == "sk-test-key"
        assert config.model == "claude-sonnet-4-20250514"
        assert config.max_tool_rounds == 5


class TestAgentConfigFromEnv:
    """Tests for from_env() class method."""

    def test_from_env_openai(self):
        """Test creating config from OpenAI environment variables."""
        env = {
            "LLM_PROVIDER": "openai",
            "OPENAI_API_KEY": "sk-openai-key",
            "OPENAI_MODEL": "gpt-4o-mini",
        }
        with patch.dict(os.environ, env, clear=False):
            config = AgentConfig.from_env()
            assert config.provider == "openai"
            assert config.api_key == "sk-openai-key"
            assert config.model == "gpt-4o-mini"

    def test_from_env_anthropic(self):
        """Test creating config from Anthropic environment variables."""
        env = {
            "LLM_PROVIDER": "anthropic",
            "ANTHROPIC_API_KEY": "sk-ant-key",
            "ANTHROPIC_MODEL": "claude-sonnet-4-20250514",
        }
        with patch.dict(os.environ, env, clear=False):
            config = AgentConfig.from_env()
            assert config.provider == "anthropic"
            assert config.api_key == "sk-ant-key"
            assert config.model == "claude-sonnet-4-20250514"

    def test_from_env_defaults(self):
        """Test from_env uses defaults when env vars are missing."""
        with patch.dict(os.environ, {}, clear=False):
            # Remove any existing env vars
            for key in ["LLM_PROVIDER", "OPENAI_API_KEY", "OPENAI_MODEL", "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL"]:
                os.environ.pop(key, None)
            config = AgentConfig.from_env()
            assert config.provider == "openai"
            assert config.api_key == ""
            assert config.model == "gpt-4o"

    def test_from_env_unknown_provider(self):
        """Test from_env with unknown provider."""
        env = {"LLM_PROVIDER": "unknown"}
        with patch.dict(os.environ, env, clear=False):
            # Remove provider-specific env vars
            for key in ["OPENAI_API_KEY", "OPENAI_MODEL", "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL"]:
                os.environ.pop(key, None)
            config = AgentConfig.from_env()
            assert config.provider == "unknown"
            assert config.api_key == ""
            assert config.model == ""

    def test_from_env_with_model(self):
        """Test from_env picks up model from env vars."""
        env = {
            "LLM_PROVIDER": "openai",
            "OPENAI_API_KEY": "sk-test",
            "OPENAI_MODEL": "gpt-3.5-turbo",
        }
        with patch.dict(os.environ, env, clear=False):
            config = AgentConfig.from_env()
            assert config.model == "gpt-3.5-turbo"
