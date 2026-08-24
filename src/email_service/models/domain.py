from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import uuid4


class FieldType(StrEnum):
    STRING = "string"
    EMAIL = "email"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ENUM = "enum"
    TEXTAREA = "textarea"


class UnknownFieldPolicy(StrEnum):
    REJECT = "reject"
    IGNORE = "ignore"


class ProviderType(StrEnum):
    SES = "ses"
    SMTP = "smtp"


class DeliveryEventType(StrEnum):
    DELIVERY = "delivery"
    BOUNCE = "bounce"
    COMPLAINT = "complaint"


@dataclass(frozen=True)
class MailAddress:
    email: str
    name: str | None = None

    def formatted(self) -> str:
        if not self.name:
            return self.email
        return f"{self.name} <{self.email}>"


@dataclass(frozen=True)
class FieldDefinition:
    name: str
    field_type: FieldType
    required: bool = False
    min_length: int | None = None
    max_length: int | None = None
    min_value: float | None = None
    max_value: float | None = None
    enum_values: tuple[str, ...] = ()


@dataclass(frozen=True)
class RateLimitPolicy:
    per_minute: int = 10
    per_day: int = 500


@dataclass(frozen=True)
class FormDefinition:
    tenant_id: str
    site_id: str
    form_id: str
    enabled: bool
    allowed_origins: tuple[str, ...]
    fields: tuple[FieldDefinition, ...]
    template_id: str
    provider_id: str
    recipient: MailAddress
    sender: MailAddress
    subject: str
    reply_to_field: str | None = None
    unknown_field_policy: UnknownFieldPolicy = UnknownFieldPolicy.REJECT
    honeypot_fields: tuple[str, ...] = ("website",)
    turnstile_required: bool = True
    rate_limit: RateLimitPolicy = field(default_factory=RateLimitPolicy)


@dataclass(frozen=True)
class Site:
    tenant_id: str
    site_id: str
    enabled: bool
    public_site_key: str


@dataclass(frozen=True)
class Tenant:
    tenant_id: str
    name: str
    enabled: bool = True


@dataclass(frozen=True)
class EmailTemplateDefinition:
    template_id: str
    version: str
    subject: str
    text_body: str
    html_body: str


@dataclass(frozen=True)
class MailProviderDefinition:
    tenant_id: str
    provider_id: str
    provider_type: ProviderType
    configuration_set: str | None = None
    smtp_secret_parameter_prefix: str | None = None


@dataclass(frozen=True)
class Submission:
    request_id: str
    tenant_id: str
    site_id: str
    form_id: str
    payload: dict[str, object]
    submitted_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass(frozen=True)
class QueuedEmailJob:
    schema_version: Literal[1]
    message_id: str
    request_id: str
    tenant_id: str
    site_id: str
    form_id: str
    submitted_at: str
    payload: dict[str, object]

    @classmethod
    def from_submission(cls, submission: Submission) -> QueuedEmailJob:
        return cls(
            schema_version=1,
            message_id=str(uuid4()),
            request_id=submission.request_id,
            tenant_id=submission.tenant_id,
            site_id=submission.site_id,
            form_id=submission.form_id,
            submitted_at=submission.submitted_at,
            payload=submission.payload,
        )


@dataclass(frozen=True)
class MailMessage:
    sender: MailAddress
    recipient: MailAddress
    subject: str
    text_body: str
    html_body: str
    reply_to: MailAddress | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SendResult:
    provider_id: str
    provider_type: ProviderType
    message_id: str
    retryable: bool = False


@dataclass(frozen=True)
class DeliveryEvent:
    event_type: DeliveryEventType
    provider_message_id: str
    occurred_at: str
    recipient: str | None = None
    reason: str | None = None
