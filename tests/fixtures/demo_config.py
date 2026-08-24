from __future__ import annotations

from email_service.models.domain import (
    EmailTemplateDefinition,
    FieldDefinition,
    FieldType,
    FormDefinition,
    MailAddress,
    MailProviderDefinition,
    ProviderType,
)
from email_service.repositories.memory import InMemoryConfigRepository


def demo_config() -> InMemoryConfigRepository:
    form = FormDefinition(
        tenant_id="demo",
        site_id="demo-hotel",
        form_id="contact",
        enabled=True,
        allowed_origins=("https://demo.example",),
        fields=(
            FieldDefinition("name", FieldType.STRING, required=True, max_length=100),
            FieldDefinition("email", FieldType.EMAIL, required=True),
            FieldDefinition("message", FieldType.TEXTAREA, required=True, max_length=1000),
        ),
        template_id="contact-v1",
        provider_id="primary-ses",
        recipient=MailAddress("owner@example.test", "Demo Owner"),
        sender=MailAddress("website@example.test", "Website Enquiry"),
        subject="New contact form submission",
        reply_to_field="email",
    )
    provider = MailProviderDefinition(
        tenant_id="demo",
        provider_id="primary-ses",
        provider_type=ProviderType.SES,
    )
    template = EmailTemplateDefinition(
        template_id="contact-v1",
        version="v1",
        subject="Contact from ${name}",
        text_body="Name: ${name}\nEmail: ${email}\nMessage: ${message}",
        html_body="<p>Name: ${name}</p><p>Email: ${email}</p><p>${message}</p>",
    )
    return InMemoryConfigRepository(
        forms={(form.site_id, form.form_id): form},
        providers={(provider.tenant_id, provider.provider_id): provider},
        templates={(provider.tenant_id, template.template_id): template},
    )
