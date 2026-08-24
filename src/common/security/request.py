from __future__ import annotations

from common.core.errors import SecurityError
from common.models.domain import FormDefinition


def validate_origin(form: FormDefinition, origin: str | None) -> None:
    if form.allowed_origins and origin not in form.allowed_origins:
        raise SecurityError("origin is not allowed")
