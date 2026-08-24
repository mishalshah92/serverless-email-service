from __future__ import annotations

import json
from typing import Any

from form_intake_lambda import main as handler


class FakeService:
    def submit(self, **kwargs: Any) -> str:
        return "req-1"


def test_api_handler_returns_accepted(monkeypatch: Any) -> None:
    monkeypatch.setattr(handler, "build_service", lambda: FakeService())

    response = handler.handle(
        {
            "pathParameters": {"form_id": "contact"},
            "headers": {"origin": "https://demo.example"},
            "requestContext": {"http": {"sourceIp": "127.0.0.1"}},
            "body": json.dumps(
                {
                    "site_id": "demo-hotel",
                    "turnstile_token": "ok",
                    "fields": {"name": "Jane"},
                }
            ),
        },
        None,
    )

    assert response["statusCode"] == 202
    assert json.loads(response["body"]) == {"request_id": "req-1", "success": True}


def test_api_handler_rejects_bad_json() -> None:
    response = handler.handle({"pathParameters": {"form_id": "contact"}, "body": "{"}, None)

    assert response["statusCode"] == 400
