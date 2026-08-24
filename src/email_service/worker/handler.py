from __future__ import annotations

from typing import Any

from email_service.core.queue_message import parse_job
from email_service.core.service import EmailWorkerService
from email_service.worker.bootstrap import provider_for, repositories


def handle(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Lambda entrypoint for queued email delivery."""
    configs, submissions = repositories()
    failures: list[dict[str, str]] = []
    for record in event.get("Records", []):
        message_id = str(record.get("messageId", ""))
        try:
            job = parse_job(str(record["body"]))
            form = configs.get_form(job.site_id, job.form_id)
            provider_definition = configs.get_provider(job.tenant_id, form.provider_id)
            service = EmailWorkerService(configs, submissions, provider_for(provider_definition))
            service.process(job)
        except Exception:
            if message_id:
                failures.append({"itemIdentifier": message_id})
    return {"batchItemFailures": failures}
