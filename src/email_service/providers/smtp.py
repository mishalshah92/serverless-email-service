from __future__ import annotations

import smtplib
from email.message import EmailMessage as MimeMessage
from typing import Protocol
from uuid import uuid4

from email_service.core.errors import ProviderError
from email_service.models.domain import MailMessage, ProviderType, SendResult


class SecretReader(Protocol):
    def get_parameter(self, name: str) -> str:
        """Read a decrypted parameter value."""
        ...


class SmtpMailProvider:
    def __init__(
        self,
        provider_id: str,
        parameter_prefix: str,
        secrets: SecretReader,
        timeout_seconds: int = 10,
    ) -> None:
        self._provider_id = provider_id
        self._prefix = parameter_prefix.rstrip("/")
        self._secrets = secrets
        self._timeout_seconds = timeout_seconds

    def send(self, message: MailMessage) -> SendResult:
        settings = self._settings()
        mime = MimeMessage()
        mime["From"] = message.sender.formatted()
        mime["To"] = message.recipient.formatted()
        mime["Subject"] = message.subject
        if message.reply_to:
            mime["Reply-To"] = message.reply_to.email
        mime.set_content(message.text_body)
        mime.add_alternative(message.html_body, subtype="html")

        try:
            with smtplib.SMTP(settings.host, settings.port, timeout=self._timeout_seconds) as smtp:
                if settings.security == "starttls":
                    smtp.starttls()
                if settings.username:
                    smtp.login(settings.username, settings.password)
                smtp.send_message(mime)
        except (OSError, smtplib.SMTPException) as exc:
            raise ProviderError("smtp send failed", retryable=True) from exc
        return SendResult(
            provider_id=self._provider_id,
            provider_type=ProviderType.SMTP,
            message_id=str(uuid4()),
        )

    def _settings(self) -> _SmtpSettings:
        return _SmtpSettings(
            host=self._secrets.get_parameter(f"{self._prefix}/host"),
            port=int(self._secrets.get_parameter(f"{self._prefix}/port")),
            username=self._secrets.get_parameter(f"{self._prefix}/username"),
            password=self._secrets.get_parameter(f"{self._prefix}/password"),
            security=self._secrets.get_parameter(f"{self._prefix}/security"),
        )


class _SmtpSettings:
    def __init__(self, host: str, port: int, username: str, password: str, security: str) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.security = security
