from __future__ import annotations

from common.events.parser import parse_ses_event
from common.models.domain import DeliveryEventType


def test_parse_ses_bounce_event() -> None:
    event = parse_ses_event(
        {
            "eventType": "Bounce",
            "mail": {"messageId": "ses-1"},
            "bounce": {
                "timestamp": "2026-08-24T00:00:00Z",
                "bounceType": "Permanent",
                "bouncedRecipients": [{"emailAddress": "bad@example.test"}],
            },
        }
    )

    assert event is not None
    assert event.event_type == DeliveryEventType.BOUNCE
    assert event.recipient == "bad@example.test"
