from __future__ import annotations

import os

from email_service.core.service import FormIntakeService
from email_service.repositories.aws import (
    DynamoConfigRepository,
    DynamoSubmissionRepository,
    SqsQueueProducer,
    SsmSecretReader,
)
from email_service.security.turnstile import CloudflareTurnstileVerifier, DisabledTurnstileVerifier


def build_service() -> FormIntakeService:
    table_name = os.environ["TABLE_NAME"]
    turnstile_parameter_name = os.environ.get("TURNSTILE_SECRET_PARAMETER_NAME", "")
    verifier = (
        CloudflareTurnstileVerifier(SsmSecretReader().get_parameter(turnstile_parameter_name))
        if turnstile_parameter_name
        else DisabledTurnstileVerifier()
    )
    return FormIntakeService(
        configs=DynamoConfigRepository(table_name),
        submissions=DynamoSubmissionRepository(table_name),
        queue=SqsQueueProducer(os.environ["QUEUE_URL"]),
        turnstile=verifier,
    )
