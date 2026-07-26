"""Email tool executor."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from src.schema.types import EmailParams

# Module-level in-memory storage with sample emails
_inbox: list[dict] = [
    {
        "id": "email_001",
        "from": "boss@company.com",
        "to": "employee@company.com",
        "subject": "Meeting Reminder - Project Review",
        "body": "Hi, this is a reminder about our project review meeting tomorrow at 10 AM. Please prepare your status update.",
        "date": "2024-01-14T09:00:00",
    },
    {
        "id": "email_002",
        "from": "hr@company.com",
        "to": "employee@company.com",
        "subject": "Leave Approval Request",
        "body": "Your leave request for January 20-22 has been approved. Please ensure proper handover before your leave.",
        "date": "2024-01-13T14:30:00",
    },
]


async def email_executor(params: EmailParams) -> Any:
    """Execute email operations.
    
    Args:
        params: Email parameters
        
    Returns:
        Email operation result
    """
    if params.action == "send":
        # Simulate sending an email
        email = {
            "id": f"email_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "from": "user@company.com",
            "to": params.to,
            "subject": params.subject,
            "body": params.body or "",
            "date": datetime.now().isoformat(),
        }
        # In a real implementation, we'd actually send the email
        # For mock, we just print to console
        print(f"📧 Email sent to {params.to}")
        print(f"   Subject: {params.subject}")
        print(f"   Body: {params.body}")
        return {"sent": True, "to": params.to, "subject": params.subject, "id": email["id"]}
    
    elif params.action == "search":
        # Search emails by query
        query = params.query.lower()
        limit = params.limit or 10
        
        matching_emails = []
        for email in _inbox:
            if (query in email["subject"].lower() or 
                query in email["body"].lower() or
                query in email["from"].lower()):
                matching_emails.append(email)
                if len(matching_emails) >= limit:
                    break
        
        return matching_emails
    
    elif params.action == "read":
        # Read a specific email
        for email in _inbox:
            if email["id"] == params.email_id:
                return email
        return {"error": "Email not found"}
    
    else:
        return {"error": f"Unknown action: {params.action}"}