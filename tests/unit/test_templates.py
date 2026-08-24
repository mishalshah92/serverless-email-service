from __future__ import annotations

from common.templates.renderer import render_mail_message
from tests.fixtures.demo_config import demo_config


def test_template_uses_backend_delivery_configuration() -> None:
    config = demo_config()
    form = config.get_form("demo-hotel", "contact")
    template = config.get_template("demo", "contact-v1")

    message = render_mail_message(
        form,
        template,
        {
            "name": "Jane",
            "email": "visitor@example.test",
            "message": "<script>alert(1)</script>",
            "recipient": "attacker@example.test",
        },
        request_id="req-1",
    )

    assert message.recipient.email == "owner@example.test"
    assert message.sender.email == "website@example.test"
    assert message.reply_to is not None
    assert message.reply_to.email == "visitor@example.test"
    assert "attacker@example.test" not in message.html_body
    assert "&lt;script&gt;" in message.html_body
