"""Calendar tool executor using local JSON file storage."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from src.schema.types import CalendarEventParams

# Data directory
DATA_DIR = Path(os.getenv("CALENDAR_DATA_DIR", "~/.wanshitong")).expanduser()
CALENDAR_FILE = DATA_DIR / "calendar.json"


def _ensure_data_dir() -> None:
    """Ensure data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_events() -> list[dict]:
    """Load events from JSON file."""
    if not CALENDAR_FILE.exists():
        return []
    try:
        with open(CALENDAR_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("events", [])
    except (json.JSONDecodeError, IOError):
        return []


def _save_events(events: list[dict]) -> None:
    """Save events to JSON file."""
    _ensure_data_dir()
    with open(CALENDAR_FILE, "w", encoding="utf-8") as f:
        json.dump({"events": events}, f, ensure_ascii=False, indent=2)


def reset_events() -> None:
    """Reset events storage (for testing)."""
    if CALENDAR_FILE.exists():
        CALENDAR_FILE.unlink()


async def calendar_executor(params: CalendarEventParams) -> str:
    """Execute calendar operations with local JSON file storage.

    Args:
        params: Calendar event parameters

    Returns:
        Human-readable result string
    """
    events = _load_events()

    if params.action == "create":
        event_id = f"evt_{uuid.uuid4().hex[:8]}"
        event = {
            "event_id": event_id,
            "title": params.title,
            "start_time": params.start_time,
            "end_time": params.end_time,
            "created_at": datetime.now().isoformat(),
        }
        events.append(event)
        _save_events(events)
        return f"事件创建成功：ID={event_id}, 标题='{params.title}', 时间={params.start_time} ~ {params.end_time}"

    elif params.action == "query":
        if not events:
            return "当前没有日程安排。"
        lines = ["当前日程："]
        for e in events:
            lines.append(f"  - [{e['event_id']}] {e['title']} ({e['start_time']} ~ {e['end_time']})")
        return "\n".join(lines)

    elif params.action == "delete":
        for i, event in enumerate(events):
            if event["event_id"] == params.event_id:
                removed = events.pop(i)
                _save_events(events)
                return f"事件已删除：{removed['title']} (ID={params.event_id})"
        return f"未找到 ID 为 {params.event_id} 的事件"

    return f"未知操作：{params.action}"