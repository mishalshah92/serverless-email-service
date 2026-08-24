from __future__ import annotations

import os

from common.core.ports import ConfigRepository, SubmissionRepository
from common.models.domain import MailProviderDefinition
from common.providers.base import MailProvider
from common.providers.factory import MailProviderFactory
from common.repositories.aws import (
    DynamoConfigRepository,
    DynamoSubmissionRepository,
    SsmSecretReader,
)


def repositories() -> tuple[ConfigRepository, SubmissionRepository]:
    table_name = os.environ["TABLE_NAME"]
    return DynamoConfigRepository(table_name), DynamoSubmissionRepository(table_name)


def provider_for(definition: MailProviderDefinition) -> MailProvider:
    return MailProviderFactory(SsmSecretReader()).create(definition)
