from __future__ import annotations

from typing import Protocol

from email_service.models.domain import MailMessage, SendResult


class MailProvider(Protocol):
    def send(self, message: MailMessage) -> SendResult:
        """Send an email message."""
        ...
