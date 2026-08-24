from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from common.models.domain import DeliveryEvent, DeliveryEventType


def parse_ses_event(payload: dict[str, Any]) -> DeliveryEvent | None:
    event_type = str(payload.get("eventType") or payload.get("notificationType") or "").lower()
    mail = payload.get("mail") or {}
    message_id = str(mail.get("messageId") or "")
    if not message_id:
        return None
    if event_type == "delivery":
        delivery = payload.get("delivery") or {}
        recipients = delivery.get("recipients") or []
        return DeliveryEvent(
            event_type=DeliveryEventType.DELIVERY,
            provider_message_id=message_id,
            occurred_at=str(delivery.get("timestamp") or _now()),
            recipient=str(recipients[0]) if recipients else None,
        )
    if event_type == "bounce":
        bounce = payload.get("bounce") or {}
        recipients = bounce.get("bouncedRecipients") or []
        recipient = recipients[0].get("emailAddress") if recipients else None
        return DeliveryEvent(
            event_type=DeliveryEventType.BOUNCE,
            provider_message_id=message_id,
            occurred_at=str(bounce.get("timestamp") or _now()),
            recipient=str(recipient) if recipient else None,
            reason=str(bounce.get("bounceType") or ""),
        )
    if event_type == "complaint":
        complaint = payload.get("complaint") or {}
        recipients = complaint.get("complainedRecipients") or []
        recipient = recipients[0].get("emailAddress") if recipients else None
        return DeliveryEvent(
            event_type=DeliveryEventType.COMPLAINT,
            provider_message_id=message_id,
            occurred_at=str(complaint.get("timestamp") or _now()),
            recipient=str(recipient) if recipient else None,
            reason="complaint",
        )
    return None


def _now() -> str:
    return datetime.now(UTC).isoformat()
