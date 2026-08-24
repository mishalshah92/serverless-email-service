from __future__ import annotations

from typing import Protocol

from common.models.domain import (
    DeliveryEvent,
    EmailTemplateDefinition,
    FormDefinition,
    MailProviderDefinition,
    QueuedEmailJob,
    SendResult,
    Submission,
)


class HealthCheck(Protocol):
    """Placeholder protocol used to verify package typing in the scaffold."""

    def ready(self) -> bool:
        """Return whether the component is ready."""
        ...


class ConfigRepository(Protocol):
    def get_form(self, site_id: str, form_id: str) -> FormDefinition:
        """Return trusted form configuration."""
        ...

    def get_provider(self, tenant_id: str, provider_id: str) -> MailProviderDefinition:
        """Return trusted provider configuration."""
        ...

    def get_template(self, tenant_id: str, template_id: str) -> EmailTemplateDefinition:
        """Return trusted email template configuration."""
        ...


class SubmissionRepository(Protocol):
    def save_submission(self, submission: Submission) -> None:
        """Record an accepted submission."""
        ...

    def record_send_result(self, job: QueuedEmailJob, result: SendResult) -> None:
        """Record successful provider send metadata."""
        ...

    def record_failure(self, job: QueuedEmailJob, reason: str) -> None:
        """Record failed provider send metadata."""
        ...

    def record_delivery_event(self, event: DeliveryEvent) -> None:
        """Record SES delivery, bounce, or complaint events."""
        ...


class QueueProducer(Protocol):
    def enqueue(self, job: QueuedEmailJob) -> None:
        """Send a validated email job to the queue."""
        ...


class TurnstileVerifier(Protocol):
    def verify(self, token: str, remote_ip: str | None, expected_hostname: str | None) -> bool:
        """Verify a Cloudflare Turnstile token."""
        ...
