"""Calendar tool executor."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from src.schema.types import CalendarEventParams

# Module-level in-memory storage
_events: list[dict] = []


async def calendar_executor(params: CalendarEventParams) -> Any:
    """Execute calendar operations.
    
    Args:
        params: Calendar event parameters
        
    Returns:
        Calendar operation result
    """
    if params.action == "create":
        # Create a new event
        event_id = f"evt_{uuid.uuid4().hex[:8]}"
        event = {
            "event_id": event_id,
            "title": params.title,
            "start_time": params.start_time,
            "end_time": params.end_time,
            "created_at": datetime.now().isoformat(),
        }
        _events.append(event)
        return event
    
    elif params.action == "query":
        # Query events (simplified - return all events for now)
        # In a real implementation, we'd filter by date_range
        return _events
    
    elif params.action == "delete":
        # Delete an event
        for i, event in enumerate(_events):
            if event["event_id"] == params.event_id:
                _events.pop(i)
                return {"deleted": True, "event_id": params.event_id}
        # If not found
        return {"deleted": False, "error": "Event not found"}
    
    else:
        return {"error": f"Unknown action: {params.action}"}