from __future__ import annotations

from email_service.models.domain import MailProviderDefinition, ProviderType
from email_service.providers.base import MailProvider
from email_service.providers.ses import SesMailProvider
from email_service.providers.smtp import SecretReader, SmtpMailProvider


class MailProviderFactory:
    def __init__(self, secrets: SecretReader | None = None) -> None:
        self._secrets = secrets

    def create(self, definition: MailProviderDefinition) -> MailProvider:
        if definition.provider_type == ProviderType.SES:
            return SesMailProvider(definition.provider_id, definition.configuration_set)
        if definition.provider_type == ProviderType.SMTP:
            if not definition.smtp_secret_parameter_prefix:
                raise ValueError("smtp provider requires smtp_secret_parameter_prefix")
            if not self._secrets:
                raise ValueError("smtp provider requires a secret reader")
            return SmtpMailProvider(
                definition.provider_id,
                definition.smtp_secret_parameter_prefix,
                self._secrets,
            )
        raise ValueError("unsupported provider type")
