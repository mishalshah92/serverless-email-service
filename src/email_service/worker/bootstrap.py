from __future__ import annotations

import os

from email_service.core.ports import ConfigRepository, SubmissionRepository
from email_service.models.domain import MailProviderDefinition
from email_service.providers.base import MailProvider
from email_service.providers.factory import MailProviderFactory
from email_service.repositories.aws import (
    DynamoConfigRepository,
    DynamoSubmissionRepository,
    SsmSecretReader,
)


def repositories() -> tuple[ConfigRepository, SubmissionRepository]:
    table_name = os.environ["TABLE_NAME"]
    return DynamoConfigRepository(table_name), DynamoSubmissionRepository(table_name)


def provider_for(definition: MailProviderDefinition) -> MailProvider:
    return MailProviderFactory(SsmSecretReader()).create(definition)
