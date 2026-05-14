"""Notification service for DevBoard."""

from email.message import EmailMessage
import logging
import os
import smtplib
from typing import Optional

logger = logging.getLogger(__name__)


async def send_status_change_notification(
    issue_id: int,
    issue_title: str,
    old_status: str,
    new_status: str,
    assignee_email: Optional[str] = None,
    reporter_email: Optional[str] = None,
) -> None:
    """Notify the issue reporter when an issue status changes."""
    logger.info(
        "[NOTIFY] Issue #%d ('%s') changed: %s -> %s | "
        "assignee=%s reporter=%s",
        issue_id,
        issue_title,
        old_status,
        new_status,
        assignee_email or "unassigned",
        reporter_email or "unknown",
    )

    if not reporter_email:
        logger.warning(
            "Skipping status change notification for issue #%d: reporter email is missing",
            issue_id,
        )
        return

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    missing = [
        name
        for name, value in {
            "SMTP_HOST": smtp_host,
            "SMTP_PORT": smtp_port,
            "SMTP_USER": smtp_user,
            "SMTP_PASS": smtp_pass,
        }.items()
        if not value
    ]
    if missing:
        logger.warning(
            "Skipping status change notification for issue #%d: missing SMTP config %s",
            issue_id,
            ", ".join(missing),
        )
        return

    try:
        port = int(smtp_port)
    except ValueError:
        logger.warning(
            "Skipping status change notification for issue #%d: SMTP_PORT must be an integer",
            issue_id,
        )
        return

    issue_link = f"http://localhost:3000/issues/{issue_id}"
    message = EmailMessage()
    message["Subject"] = f"[DevBoard] Issue #{issue_id} status changed"
    message["From"] = smtp_user
    message["To"] = reporter_email
    message.set_content(
        "\n".join(
            [
                f"Issue: {issue_title}",
                f"Old status: {old_status}",
                f"New status: {new_status}",
                f"Link: {issue_link}",
            ]
        )
    )

    try:
        with smtplib.SMTP(smtp_host, port) as smtp:
            smtp.starttls()
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException):
        logger.exception(
            "Failed to send status change notification for issue #%d",
            issue_id,
        )
