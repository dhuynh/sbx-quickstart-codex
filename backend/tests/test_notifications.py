from unittest.mock import MagicMock, patch

import pytest

from app.services.notifications import send_status_change_notification


@pytest.mark.asyncio
async def test_send_status_change_notification_sends_email(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "devboard@example.com")
    monkeypatch.setenv("SMTP_PASS", "secret")

    smtp = MagicMock()
    smtp_context = MagicMock()
    smtp_context.__enter__.return_value = smtp

    with patch("app.services.notifications.smtplib.SMTP", return_value=smtp_context) as smtp_cls:
        await send_status_change_notification(
            issue_id=42,
            issue_title="Login fails",
            old_status="open",
            new_status="in_progress",
            reporter_email="reporter@example.com",
        )

    smtp_cls.assert_called_once_with("smtp.example.com", 587)
    smtp.starttls.assert_called_once_with()
    smtp.login.assert_called_once_with("devboard@example.com", "secret")
    smtp.send_message.assert_called_once()

    message = smtp.send_message.call_args.args[0]
    assert message["To"] == "reporter@example.com"
    assert message["From"] == "devboard@example.com"
    assert message["Subject"] == "[DevBoard] Issue #42 status changed"
    body = message.get_content()
    assert "Issue: Login fails" in body
    assert "Old status: open" in body
    assert "New status: in_progress" in body
    assert "Link: http://localhost:3000/issues/42" in body
