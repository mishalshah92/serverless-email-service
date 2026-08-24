from __future__ import annotations

import json
import os
from typing import Any

from email_service.events.parser import parse_ses_event
from email_service.repositories.aws import DynamoSubmissionRepository


def handle(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Lambda entrypoint for SES delivery, bounce, and complaint events."""
    repository = DynamoSubmissionRepository(os.environ["TABLE_NAME"])
    count = 0
    for record in event.get("Records", []):
        body = record.get("Sns", {}).get("Message") or record.get("body") or "{}"
        payload = json.loads(str(body))
        delivery_event = parse_ses_event(payload)
        if delivery_event:
            repository.record_delivery_event(delivery_event)
            count += 1
    return {"recorded": count}
