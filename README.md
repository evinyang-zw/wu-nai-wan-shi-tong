# 吾乃万事通 — 个人助手 Agent

基于 LLM Function Calling 的个人助手 Agent，支持日历、邮件、天气、搜索等工具调用。重点展示 **Function Calling 机制** 和 **工具 Schema 设计**。

## 特性

- **多 LLM 支持**：OpenAI (GPT-4o) / Anthropic (Claude) / 小米 (MiMo-v2.5)，可扩展更多 Provider
- **自定义 Base URL**：支持 OpenAI 兼容的第三方 API 端点
- **工具 Schema 设计**：基于 Pydantic 的类型安全参数定义，自动转换为 LLM 工具格式
- **Function Calling 流程**：LLM 自主决策工具选择、参数生成、结果整合
- **多轮工具调用**：支持单轮多工具并行、多轮串联、错误降级
- **Mock + 真实 API 预留**：默认 Mock 实现，可无缝切换真实 API

## 架构

```
用户输入 → LLM 分析意图 → 调用工具？
                          ├── 是 → 执行工具 → 结果回传 LLM → 最终回答
                          └── 否 → 直接回答
```

## 项目结构

```
src/
├── main.py                 # CLI 入口
├── agent/
│   ├── core.py             # Agent 核心对话循环
│   └── config.py           # 运行时配置
├── llm/
│   ├── base.py             # LLM Provider 抽象接口
│   ├── openai_provider.py  # OpenAI Function Calling
│   ├── anthropic_provider.py  # Anthropic Tool Use
│   └── factory.py          # Provider 工厂
├── schema/
│   └── types.py            # 工具参数 Schema（Pydantic）
└── tools/
    ├── base.py             # Schema → LLM 格式转换
    ├── calendar.py         # 日历工具
    ├── email_tool.py       # 邮件工具
    ├── weather.py          # 天气工具
    ├── search.py           # 搜索工具
    └── registry.py         # 工具注册中心
```

## 快速开始

### 安装依赖

```bash
pip install -e .
```

或使用 uv：

```bash
uv sync
```

### 配置

复制环境变量模板并填入 API Key：

```bash
cp .env.example .env
```

编辑 `.env`：

```env
# 选择 LLM Provider
LLM_PROVIDER=openai

# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o

# 或 Anthropic
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-your-key-here
# ANTHROPIC_MODEL=claude-sonnet-4-20250514

# 或小米 MiMo（自定义 Base URL）
# LLM_PROVIDER=xiaomi
# LLM_API_KEY=sk-your-key-here
# LLM_MODEL=mimo-v2.5
# LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

### 运行

```bash
python -m src.main
```

### 示例对话

```
你: 帮我查一下北京今天的天气
万事通: 北京今天天气晴朗，气温 28°C，湿度 45%，适合外出活动。

你: 明天上午10点帮我创建一个会议
万事通: 已创建会议：明天 10:00-11:00，事件 ID: evt_001。

你: 今天天气怎么样？如果下雨就帮我创建一个室内活动
万事通: 今天有小雨，已帮你创建室内读书会，时间 10:00-12:00。
```

## 工具 Schema 设计

每个工具通过 Pydantic 模型定义参数，自动转换为 LLM 工具格式：

```python
class WeatherParams(BaseModel):
    """天气查询参数"""
    city: NonEmptyStr = Field(..., description="城市名称")
    include_forecast: bool = Field(False, description="是否包含预报")
    forecast_days: Annotated[int, Field(ge=1, le=7)] = Field(3, description="预报天数")
```

Schema 设计原则：
- 每个字段必须有 `description`，LLM 靠它理解参数含义
- 必填参数用 `Field(...)`，可选参数设默认值
- 固定选项用 `Literal` 枚举
- 类型要精确，避免 `Any`
- 复杂结构用嵌套 `BaseModel`

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_schema.py      # Schema 校验测试
pytest tests/test_tools.py       # 工具执行测试
pytest tests/test_agent.py       # Agent 集成测试
```

## 扩展

### 添加新工具

1. 在 `src/schema/types.py` 定义参数 Schema
2. 在 `src/tools/` 实现执行函数
3. 在 `src/main.py` 的 `build_registry()` 中注册

```python
registry.register(
    name="my_tool",
    schema=MyToolParams,
    description="工具描述",
    executor=my_tool_executor,
)
```

### 切换 LLM Provider

修改 `.env` 中的 `LLM_PROVIDER` 即可，无需修改代码。支持：

- **OpenAI**：`LLM_PROVIDER=openai`（使用 `OPENAI_API_KEY`）
- **Anthropic**：`LLM_PROVIDER=anthropic`（使用 `ANTHROPIC_API_KEY`）
- **自定义 API**：`LLM_PROVIDER=<任意名称>`（使用 `LLM_API_KEY` + `LLM_BASE_URL`）

## License

MIT
