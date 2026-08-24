from __future__ import annotations

import html
import re
from datetime import datetime

from common.core.errors import ValidationError
from common.models.domain import (
    FieldDefinition,
    FieldType,
    FormDefinition,
    UnknownFieldPolicy,
)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_BODY_BYTES = 64_000
MAX_STRING_LENGTH = 4_000


def validate_payload_size(body: str, max_bytes: int = MAX_BODY_BYTES) -> None:
    if len(body.encode("utf-8")) > max_bytes:
        raise ValidationError("request body is too large")


def validate_form_payload(form: FormDefinition, payload: dict[str, object]) -> dict[str, object]:
    for honeypot in form.honeypot_fields:
        if str(payload.get(honeypot, "")).strip():
            raise ValidationError("invalid submission")

    definitions = {field.name: field for field in form.fields}
    unknown = set(payload) - set(definitions) - set(form.honeypot_fields) - {"turnstile_token"}
    if unknown and form.unknown_field_policy == UnknownFieldPolicy.REJECT:
        raise ValidationError("unknown fields are not allowed")

    normalized: dict[str, object] = {}
    for field in form.fields:
        raw = payload.get(field.name)
        if _is_missing(raw):
            if field.required:
                raise ValidationError(f"{field.name} is required")
            continue
        normalized[field.name] = _validate_field(field, raw)
    return normalized


def escape_template_value(value: object) -> str:
    return html.escape(str(value), quote=True)


def reject_header_injection(value: str, field_name: str) -> None:
    if "\r" in value or "\n" in value:
        raise ValidationError(f"{field_name} contains invalid characters")


def _validate_field(field: FieldDefinition, raw: object) -> object:
    if field.field_type in {FieldType.STRING, FieldType.TEXTAREA, FieldType.EMAIL, FieldType.ENUM}:
        value = str(raw).strip()
        reject_header_injection(value, field.name)
        max_length = field.max_length or (
            MAX_STRING_LENGTH if field.field_type == FieldType.TEXTAREA else 512
        )
        if len(value) > max_length:
            raise ValidationError(f"{field.name} is too long")
        if field.min_length is not None and len(value) < field.min_length:
            raise ValidationError(f"{field.name} is too short")
        if field.field_type == FieldType.EMAIL and not EMAIL_RE.match(value):
            raise ValidationError(f"{field.name} must be a valid email")
        if field.field_type == FieldType.ENUM and value not in field.enum_values:
            raise ValidationError(f"{field.name} is not an allowed value")
        return value

    if field.field_type == FieldType.INTEGER:
        int_value = int(str(raw))
        _validate_number_range(field, float(int_value))
        return int_value

    if field.field_type == FieldType.NUMBER:
        number_value = float(str(raw))
        _validate_number_range(field, number_value)
        return number_value

    if field.field_type == FieldType.BOOLEAN:
        if isinstance(raw, bool):
            return raw
        if str(raw).lower() in {"true", "1", "yes"}:
            return True
        if str(raw).lower() in {"false", "0", "no"}:
            return False
        raise ValidationError(f"{field.name} must be a boolean")

    if field.field_type == FieldType.DATE:
        return datetime.strptime(str(raw), "%Y-%m-%d").date().isoformat()

    if field.field_type == FieldType.DATETIME:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00")).isoformat()

    raise ValidationError(f"{field.name} has unsupported field type")


def _validate_number_range(field: FieldDefinition, value: float) -> None:
    if field.min_value is not None and value < field.min_value:
        raise ValidationError(f"{field.name} is too small")
    if field.max_value is not None and value > field.max_value:
        raise ValidationError(f"{field.name} is too large")


def _is_missing(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())
