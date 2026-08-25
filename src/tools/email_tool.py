"""Email tool executor using SMTP for sending and local JSON for storage."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from pathlib import Path

import aiosmtplib
from email.message import EmailMessage

from src.schema.types import EmailParams

# Data directory
DATA_DIR = Path(os.getenv("CALENDAR_DATA_DIR", "~/.wanshitong")).expanduser()
INBOX_FILE = DATA_DIR / "inbox.json"

# SMTP configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)


def _ensure_data_dir() -> None:
    """Ensure data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_inbox() -> list[dict]:
    """Load inbox from JSON file."""
    if not INBOX_FILE.exists():
        return []
    try:
        with open(INBOX_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("emails", [])
    except (json.JSONDecodeError, IOError):
        return []


def _save_inbox(emails: list[dict]) -> None:
    """Save inbox to JSON file."""
    _ensure_data_dir()
    with open(INBOX_FILE, "w", encoding="utf-8") as f:
        json.dump({"emails": emails}, f, ensure_ascii=False, indent=2)


def reset_inbox() -> None:
    """Reset inbox storage (for testing)."""
    if INBOX_FILE.exists():
        INBOX_FILE.unlink()


async def _send_email(to: str, subject: str, body: str) -> str:
    """Send email via SMTP."""
    if not SMTP_USER or not SMTP_PASSWORD:
        return "邮件发送失败：未配置 SMTP 凭证。请在 .env 文件中设置 SMTP_USER 和 SMTP_PASSWORD。"

    message = EmailMessage()
    message["From"] = SMTP_FROM
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            use_tls=True,
        )
        return None  # Success
    except Exception as e:
        return f"邮件发送失败: {str(e)}"


async def email_executor(params: EmailParams) -> str:
    """Execute email operations.

    Args:
        params: Email parameters

    Returns:
        Human-readable result string
    """
    if params.action == "send":
        # Send email via SMTP
        error = await _send_email(params.to, params.subject, params.body)
        if error:
            return error

        # Save to local inbox
        email_id = f"email_{uuid.uuid4().hex[:8]}"
        emails = _load_inbox()
        emails.append({
            "id": email_id,
            "from": SMTP_FROM,
            "to": params.to,
            "subject": params.subject,
            "body": params.body,
            "date": datetime.now().isoformat(),
            "sent": True,
        })
        _save_inbox(emails)

        return f"邮件发送成功：ID={email_id}, 收件人={params.to}, 主题='{params.subject}'"

    elif params.action == "search":
        emails = _load_inbox()
        query = params.query.lower()
        limit = params.limit or 10

        matching_emails = []
        for email in emails:
            if (query in email.get("subject", "").lower() or
                    query in email.get("body", "").lower() or
                    query in email.get("from", "").lower()):
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
        emails = _load_inbox()
        for email in emails:
            if email["id"] == params.email_id:
                return (f"邮件详情：\n"
                        f"发件人: {email['from']}\n"
                        f"收件人: {email['to']}\n"
                        f"主题: {email['subject']}\n"
                        f"日期: {email['date']}\n"
                        f"内容: {email['body']}")
        return f"未找到 ID 为 {params.email_id} 的邮件"

    return f"未知操作：{params.action}"