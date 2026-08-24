from __future__ import annotations

import pytest

from common.core.errors import ValidationError
from common.core.validation import validate_form_payload
from tests.fixtures.demo_config import demo_config


def test_valid_payload_is_normalized() -> None:
    form = demo_config().get_form("demo-hotel", "contact")

    payload = validate_form_payload(
        form,
        {"name": " Jane ", "email": "jane@example.test", "message": "Hello"},
    )

    assert payload == {"name": "Jane", "email": "jane@example.test", "message": "Hello"}


def test_unknown_delivery_fields_are_rejected() -> None:
    form = demo_config().get_form("demo-hotel", "contact")

    with pytest.raises(ValidationError):
        validate_form_payload(
            form,
            {
                "name": "Jane",
                "email": "jane@example.test",
                "message": "Hello",
                "recipient": "attacker@example.test",
            },
        )


def test_header_injection_is_rejected() -> None:
    form = demo_config().get_form("demo-hotel", "contact")

    with pytest.raises(ValidationError):
        validate_form_payload(
            form,
            {"name": "Jane", "email": "jane@example.test\r\nBcc: x@y.test", "message": "Hi"},
        )


def test_honeypot_is_rejected() -> None:
    form = demo_config().get_form("demo-hotel", "contact")

    with pytest.raises(ValidationError):
        validate_form_payload(
            form,
            {
                "name": "Jane",
                "email": "jane@example.test",
                "message": "Hello",
                "website": "filled",
            },
        )
