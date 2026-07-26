"""Email tool executor."""
from __future__ import annotations

from datetime import datetime

from src.schema.types import EmailParams

# Module-level in-memory storage with sample emails
_inbox: list[dict] = [
    {
        "id": "email_001",
        "from": "boss@company.com",
        "to": "employee@company.com",
        "subject": "会议提醒 - 项目评审",
        "body": "你好，明天上午10点有项目评审会议，请准备好状态更新。",
        "date": "2024-01-14T09:00:00",
    },
    {
        "id": "email_002",
        "from": "hr@company.com",
        "to": "employee@company.com",
        "subject": "年假申请已批准",
        "body": "您1月20-22日的年假申请已批准。请在休假前做好交接。",
        "date": "2024-01-13T14:30:00",
    },
]


def reset_inbox() -> None:
    """Reset inbox storage (for testing)."""
    _inbox.clear()
    _inbox.extend([
        {
            "id": "email_001",
            "from": "boss@company.com",
            "to": "employee@company.com",
            "subject": "会议提醒 - 项目评审",
            "body": "你好，明天上午10点有项目评审会议，请准备好状态更新。",
            "date": "2024-01-14T09:00:00",
        },
        {
            "id": "email_002",
            "from": "hr@company.com",
            "to": "employee@company.com",
            "subject": "年假申请已批准",
            "body": "您1月20-22日的年假申请已批准。请在休假前做好交接。",
            "date": "2024-01-13T14:30:00",
        },
    ])


async def email_executor(params: EmailParams) -> str:
    """Execute email operations.

    Args:
        params: Email parameters

    Returns:
        Human-readable result string
    """
    if params.action == "send":
        email_id = f"email_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return f"邮件发送成功：ID={email_id}, 收件人={params.to}, 主题='{params.subject}'"

    elif params.action == "search":
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

        if not matching_emails:
            return f"未找到与 '{params.query}' 相关的邮件。"
        lines = [f"找到 {len(matching_emails)} 封邮件："]
        for e in matching_emails:
            lines.append(f"  - [{e['id']}] {e['subject']} (来自 {e['from']}, {e['date']})")
        return "\n".join(lines)

    elif params.action == "read":
        for email in _inbox:
            if email["id"] == params.email_id:
                return f"邮件详情：\n发件人: {email['from']}\n主题: {email['subject']}\n日期: {email['date']}\n内容: {email['body']}"
        return f"未找到 ID 为 {params.email_id} 的邮件"

    return f"未知操作：{params.action}"
