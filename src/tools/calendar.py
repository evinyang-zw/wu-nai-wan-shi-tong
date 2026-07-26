"""Calendar tool executor."""
from __future__ import annotations

import uuid
from datetime import datetime

from src.schema.types import CalendarEventParams

# Module-level in-memory storage
_events: list[dict] = []


def reset_events() -> None:
    """Reset events storage (for testing)."""
    _events.clear()


async def calendar_executor(params: CalendarEventParams) -> str:
    """Execute calendar operations.

    Args:
        params: Calendar event parameters

    Returns:
        Human-readable result string
    """
    if params.action == "create":
        event_id = f"evt_{uuid.uuid4().hex[:8]}"
        event = {
            "event_id": event_id,
            "title": params.title,
            "start_time": params.start_time,
            "end_time": params.end_time,
            "created_at": datetime.now().isoformat(),
        }
        _events.append(event)
        return f"事件创建成功：ID={event_id}, 标题='{params.title}', 时间={params.start_time} ~ {params.end_time}"

    elif params.action == "query":
        if not _events:
            return "当前没有日程安排。"
        lines = ["当前日程："]
        for e in _events:
            lines.append(f"  - [{e['event_id']}] {e['title']} ({e['start_time']} ~ {e['end_time']})")
        return "\n".join(lines)

    elif params.action == "delete":
        for i, event in enumerate(_events):
            if event["event_id"] == params.event_id:
                removed = _events.pop(i)
                return f"事件已删除：{removed['title']} (ID={params.event_id})"
        return f"未找到 ID 为 {params.event_id} 的事件"

    return f"未知操作：{params.action}"
