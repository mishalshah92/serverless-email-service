from __future__ import annotations

import json
from typing import Any

from email_service.api.bootstrap import build_service
from email_service.core.errors import EmailServiceError, ValidationError
from email_service.core.validation import validate_payload_size


def handle(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Lambda entrypoint for public form intake."""
    try:
        body = str(event.get("body") or "")
        validate_payload_size(body)
        payload = json.loads(body)
        if not isinstance(payload, dict):
            raise ValidationError("request body must be a json object")
        path = event.get("pathParameters") or {}
        form_id = str(path.get("form_id") or path.get("formId") or "")
        site_id = str(payload.get("site_id") or "")
        fields = payload.get("fields") or {}
        if not form_id or not site_id or not isinstance(fields, dict):
            raise ValidationError("site_id, form_id, and fields are required")
        turnstile_token = payload.get("turnstile_token")
        if turnstile_token:
            fields["turnstile_token"] = turnstile_token
        request_context = event.get("requestContext") or {}
        http = request_context.get("http") or {}
        request_id = build_service().submit(
            site_id=site_id,
            form_id=form_id,
            payload=dict(fields),
            origin=_header(event, "origin"),
            remote_ip=http.get("sourceIp"),
            expected_hostname=_header(event, "host"),
        )
        return _response(202, {"success": True, "request_id": request_id})
    except EmailServiceError as exc:
        return _response(exc.status_code, {"success": False, "error": {"code": exc.public_code}})
    except (json.JSONDecodeError, TypeError, ValueError):
        return _response(400, {"success": False, "error": {"code": "validation_failed"}})


def _header(event: dict[str, Any], name: str) -> str | None:
    headers = event.get("headers") or {}
    for key, value in headers.items():
        if str(key).lower() == name:
            return str(value)
    return None


def _response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(body, sort_keys=True),
    }
