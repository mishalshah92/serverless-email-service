from __future__ import annotations

from string import Template

from common.core.validation import escape_template_value, reject_header_injection
from common.models.domain import (
    EmailTemplateDefinition,
    FormDefinition,
    MailAddress,
    MailMessage,
)


def render_mail_message(
    form: FormDefinition,
    template: EmailTemplateDefinition,
    payload: dict[str, object],
    *,
    request_id: str,
) -> MailMessage:
    values = {key: escape_template_value(value) for key, value in payload.items()}
    subject = _render_subject(template.subject or form.subject, values)
    reply_to = _reply_to(form, payload)
    return MailMessage(
        sender=form.sender,
        recipient=form.recipient,
        reply_to=reply_to,
        subject=subject,
        text_body=_render(template.text_body, values),
        html_body=_render(template.html_body, values),
        metadata={"request_id": request_id, "site_id": form.site_id, "form_id": form.form_id},
    )


def _render(source: str, values: dict[str, str]) -> str:
    return Template(source).safe_substitute(values)


def _render_subject(source: str, values: dict[str, str]) -> str:
    subject = _render(source, values)
    reject_header_injection(subject, "subject")
    return subject[:200]


def _reply_to(form: FormDefinition, payload: dict[str, object]) -> MailAddress | None:
    if not form.reply_to_field:
        return None
    value = str(payload.get(form.reply_to_field, "")).strip()
    if not value:
        return None
    reject_header_injection(value, "reply_to")
    return MailAddress(email=value)
