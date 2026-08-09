# Agent Instructions

## Project Overview
Personal assistant Agent based on LLM Function Calling. Supports OpenAI (GPT-4o) and Anthropic (Claude) providers.

## Quick Start
```bash
# Install dependencies
uv sync

# Run the assistant
python -m src.main

# Run tests
uv run pytest
```

## Environment Setup
Copy `.env.example` to `.env` and configure:
- `LLM_PROVIDER`: `openai` or `anthropic`
- API key for the chosen provider
- Model name (defaults provided in `.env.example`)

**Note**: The app will exit with an error if API key is not configured.

## Architecture

```
User Input → LLM analyzes intent → Call tool?
                                 ├── Yes → Execute tool → Return result to LLM → Final answer
                                 └── No → Direct answer
```

Key components:
- `src/agent/core.py`: Main conversation loop with multi-round tool calling
- `src/llm/factory.py`: Provider factory pattern (lazy imports)
- `src/tools/registry.py`: Tool registration and execution
- `src/schema/types.py`: Pydantic models for tool parameters

## Tool Development Pattern

1. Define parameter schema in `src/schema/types.py` using Pydantic
2. Implement executor function in `src/tools/<tool>.py`
3. Register in `src/main.py:build_registry()`

**Schema rules**: Every field must have `description` for LLM understanding. Use `Field(...)` for required params. Use `Literal` for fixed options.

## Testing

```bash
# All tests (77 tests, ~2.5s)
uv run pytest

# Specific test files
uv run pytest tests/test_agent.py
uv run pytest tests/test_tools.py
uv run pytest tests/test_schema.py

# Verbose output
uv run pytest -v
```

**Note**: Tests use `asyncio_mode = "auto"` (configured in `pyproject.toml`).

## Project Structure

```
src/
├── main.py                 # CLI entry point, tool registration
├── agent/
│   ├── core.py             # Conversation loop, multi-round tool calling
│   └── config.py           # Runtime config from env vars
├── llm/
│   ├── base.py             # Abstract LLM interface
│   ├── openai_provider.py  # OpenAI Function Calling
│   ├── anthropic_provider.py  # Anthropic Tool Use
│   └── factory.py          # Provider factory (lazy imports)
├── schema/
│   └── types.py            # Pydantic tool parameter schemas
└── tools/
    ├── base.py             # Schema → LLM format conversion
    ├── calendar.py         # Calendar tool (mock)
    ├── email_tool.py       # Email tool (mock)
    ├── weather.py          # Weather tool (mock)
    ├── search.py           # Search tool (mock)
    └── registry.py         # Tool registry
```

## Key Conventions

- **Language**: Code comments and docstrings in English, user-facing messages in Chinese
- **Type Safety**: Use Pydantic models for all tool parameters, never `Any`
- **Error Handling**: Tool errors are caught and passed back to LLM for graceful degradation
- **Testing**: All tools have mock implementations; tests verify schema validation and execution flow
- **Provider Pattern**: LLM providers use factory pattern with lazy imports to avoid loading unused dependencies

## Common Pitfalls

1. **Missing API Key**: App exits immediately if `LLM_PROVIDER` env var is set but corresponding API key is missing
2. **Tool Schema**: Forgetting `description` on fields makes LLM unable to understand parameters
3. **Async Executors**: All tool executors must be `async` functions
4. **Mock vs Real**: Tools currently use mock implementations; when adding real APIs, keep mock as fallback