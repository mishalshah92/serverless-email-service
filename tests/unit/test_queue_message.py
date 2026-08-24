from __future__ import annotations

from common.core.queue_message import parse_job, serialize_job
from common.models.domain import QueuedEmailJob


def test_queue_message_round_trip_has_no_credentials() -> None:
    job = QueuedEmailJob(
        schema_version=1,
        message_id="msg-1",
        request_id="req-1",
        tenant_id="tenant",
        site_id="site",
        form_id="contact",
        submitted_at="2026-08-24T00:00:00+00:00",
        payload={"name": "Jane"},
    )

    body = serialize_job(job)
    parsed = parse_job(body)

    assert parsed == job
    assert "password" not in body
    assert "recipient" not in body
    assert "template_id" not in body
