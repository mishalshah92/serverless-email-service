from __future__ import annotations

import json
from typing import Any

from common.core.errors import NotFoundError
from common.core.queue_message import serialize_job
from common.models.domain import (
    DeliveryEvent,
    EmailTemplateDefinition,
    FieldDefinition,
    FieldType,
    FormDefinition,
    MailAddress,
    MailProviderDefinition,
    ProviderType,
    QueuedEmailJob,
    SendResult,
    Submission,
)


class DynamoConfigRepository:
    def __init__(self, table_name: str, dynamodb_resource: Any | None = None) -> None:
        self._table = (dynamodb_resource or _boto3_resource("dynamodb")).Table(table_name)

    def get_form(self, site_id: str, form_id: str) -> FormDefinition:
        item = self._get(f"SITE#{site_id}", f"FORM#{form_id}")
        fields = tuple(
            FieldDefinition(
                name=str(field["name"]),
                field_type=FieldType(str(field["type"])),
                required=bool(field.get("required", False)),
                max_length=int(field["max_length"]) if field.get("max_length") else None,
                enum_values=tuple(field.get("enum_values", ())),
            )
            for field in item.get("fields", ())
        )
        return FormDefinition(
            tenant_id=str(item["tenant_id"]),
            site_id=site_id,
            form_id=form_id,
            enabled=bool(item.get("enabled", True)),
            allowed_origins=tuple(item.get("allowed_origins", ())),
            fields=fields,
            template_id=str(item["template_id"]),
            provider_id=str(item["provider_id"]),
            recipient=MailAddress(email=str(item["recipient"])),
            sender=_address(str(item["sender"])),
            subject=str(item.get("subject", "New website submission")),
            reply_to_field=item.get("reply_to_field"),
        )

    def get_provider(self, tenant_id: str, provider_id: str) -> MailProviderDefinition:
        item = self._get(f"TENANT#{tenant_id}", f"PROVIDER#{provider_id}")
        return MailProviderDefinition(
            tenant_id=tenant_id,
            provider_id=provider_id,
            provider_type=ProviderType(str(item["provider_type"])),
            configuration_set=item.get("configuration_set"),
            smtp_secret_parameter_prefix=item.get("smtp_secret_parameter_prefix"),
        )

    def get_template(self, tenant_id: str, template_id: str) -> EmailTemplateDefinition:
        item = self._get(f"TENANT#{tenant_id}", f"TEMPLATE#{template_id}")
        return EmailTemplateDefinition(
            template_id=template_id,
            version=str(item.get("version", "v1")),
            subject=str(item["subject"]),
            text_body=str(item["text_body"]),
            html_body=str(item["html_body"]),
        )

    def _get(self, pk: str, sk: str) -> dict[str, Any]:
        item = self._table.get_item(Key={"pk": pk, "sk": sk}).get("Item")
        if not item:
            raise NotFoundError("configuration item was not found")
        return dict(item)


class DynamoSubmissionRepository:
    def __init__(self, table_name: str, dynamodb_resource: Any | None = None) -> None:
        self._table = (dynamodb_resource or _boto3_resource("dynamodb")).Table(table_name)

    def save_submission(self, submission: Submission) -> None:
        self._table.put_item(
            Item={
                "pk": f"SUBMISSION#{submission.request_id}",
                "sk": "STATUS",
                "request_id": submission.request_id,
                "tenant_id": submission.tenant_id,
                "site_id": submission.site_id,
                "form_id": submission.form_id,
                "submitted_at": submission.submitted_at,
                "status": "queued",
            }
        )

    def record_send_result(self, job: QueuedEmailJob, result: SendResult) -> None:
        self._table.update_item(
            Key={"pk": f"SUBMISSION#{job.request_id}", "sk": "STATUS"},
            UpdateExpression="SET #status=:s, provider_message_id=:m, provider_type=:p",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":s": "sent",
                ":m": result.message_id,
                ":p": result.provider_type.value,
            },
        )

    def record_failure(self, job: QueuedEmailJob, reason: str) -> None:
        self._table.update_item(
            Key={"pk": f"SUBMISSION#{job.request_id}", "sk": "STATUS"},
            UpdateExpression="SET #status=:s, failure_reason=:r",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={":s": "failed", ":r": reason[:500]},
        )

    def record_delivery_event(self, event: DeliveryEvent) -> None:
        self._table.put_item(
            Item={
                "pk": f"PROVIDER_MESSAGE#{event.provider_message_id}",
                "sk": f"EVENT#{event.occurred_at}",
                "event_type": event.event_type.value,
                "recipient": event.recipient,
                "reason": event.reason,
            }
        )


class SqsQueueProducer:
    def __init__(self, queue_url: str, sqs_client: Any | None = None) -> None:
        self._queue_url = queue_url
        self._sqs = sqs_client or _boto3_client("sqs")

    def enqueue(self, job: QueuedEmailJob) -> None:
        self._sqs.send_message(QueueUrl=self._queue_url, MessageBody=serialize_job(job))


class SsmSecretReader:
    def __init__(self, ssm_client: Any | None = None) -> None:
        self._ssm = ssm_client or _boto3_client("ssm")
        self._cache: dict[str, str] = {}

    def get_parameter(self, name: str) -> str:
        if name not in self._cache:
            response = self._ssm.get_parameter(Name=name, WithDecryption=True)
            self._cache[name] = str(response["Parameter"]["Value"])
        return self._cache[name]


def _address(raw: str) -> MailAddress:
    if "<" in raw and raw.endswith(">"):
        name, email = raw.rsplit("<", 1)
        return MailAddress(email=email.rstrip(">").strip(), name=name.strip())
    return MailAddress(email=raw)


def _boto3_client(service: str) -> Any:
    import boto3  # type: ignore[import-not-found]

    return boto3.client(service)


def _boto3_resource(service: str) -> Any:
    import boto3

    return boto3.resource(service)


def item_to_json(item: dict[str, Any]) -> str:
    return json.dumps(item, sort_keys=True, default=str)
