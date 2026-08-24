from __future__ import annotations

from dataclasses import dataclass, field

from common.core.errors import NotFoundError
from common.models.domain import (
    DeliveryEvent,
    EmailTemplateDefinition,
    FormDefinition,
    MailProviderDefinition,
    QueuedEmailJob,
    SendResult,
    Submission,
)


@dataclass
class InMemoryConfigRepository:
    forms: dict[tuple[str, str], FormDefinition] = field(default_factory=dict)
    providers: dict[tuple[str, str], MailProviderDefinition] = field(default_factory=dict)
    templates: dict[tuple[str, str], EmailTemplateDefinition] = field(default_factory=dict)

    def get_form(self, site_id: str, form_id: str) -> FormDefinition:
        try:
            return self.forms[(site_id, form_id)]
        except KeyError as exc:
            raise NotFoundError("form was not found") from exc

    def get_provider(self, tenant_id: str, provider_id: str) -> MailProviderDefinition:
        try:
            return self.providers[(tenant_id, provider_id)]
        except KeyError as exc:
            raise NotFoundError("provider was not found") from exc

    def get_template(self, tenant_id: str, template_id: str) -> EmailTemplateDefinition:
        try:
            return self.templates[(tenant_id, template_id)]
        except KeyError as exc:
            raise NotFoundError("template was not found") from exc


@dataclass
class InMemorySubmissionRepository:
    submissions: list[Submission] = field(default_factory=list)
    send_results: list[tuple[QueuedEmailJob, SendResult]] = field(default_factory=list)
    failures: list[tuple[QueuedEmailJob, str]] = field(default_factory=list)
    delivery_events: list[DeliveryEvent] = field(default_factory=list)

    def save_submission(self, submission: Submission) -> None:
        self.submissions.append(submission)

    def record_send_result(self, job: QueuedEmailJob, result: SendResult) -> None:
        self.send_results.append((job, result))

    def record_failure(self, job: QueuedEmailJob, reason: str) -> None:
        self.failures.append((job, reason))

    def record_delivery_event(self, event: DeliveryEvent) -> None:
        self.delivery_events.append(event)
