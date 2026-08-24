from __future__ import annotations

import json
from typing import Any

from common.core.errors import ValidationError
from common.models.domain import QueuedEmailJob


def serialize_job(job: QueuedEmailJob) -> str:
    return json.dumps(
        {
            "schema_version": job.schema_version,
            "message_id": job.message_id,
            "request_id": job.request_id,
            "tenant_id": job.tenant_id,
            "site_id": job.site_id,
            "form_id": job.form_id,
            "submitted_at": job.submitted_at,
            "payload": job.payload,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def parse_job(body: str) -> QueuedEmailJob:
    try:
        data: dict[str, Any] = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValidationError("invalid queue message json") from exc

    if data.get("schema_version") != 1:
        raise ValidationError("unsupported queue message schema")
    return QueuedEmailJob(
        schema_version=1,
        message_id=str(data["message_id"]),
        request_id=str(data["request_id"]),
        tenant_id=str(data["tenant_id"]),
        site_id=str(data["site_id"]),
        form_id=str(data["form_id"]),
        submitted_at=str(data["submitted_at"]),
        payload=dict(data["payload"]),
    )
