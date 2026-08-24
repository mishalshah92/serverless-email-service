from __future__ import annotations


class EmailServiceError(Exception):
    public_code = "internal_error"
    status_code = 500


class NotFoundError(EmailServiceError):
    public_code = "not_found"
    status_code = 404


class DisabledError(EmailServiceError):
    public_code = "disabled"
    status_code = 403


class ValidationError(EmailServiceError):
    public_code = "validation_failed"
    status_code = 400


class SecurityError(EmailServiceError):
    public_code = "forbidden"
    status_code = 403


class RateLimitError(EmailServiceError):
    public_code = "rate_limited"
    status_code = 429


class ProviderError(EmailServiceError):
    def __init__(self, message: str, *, retryable: bool) -> None:
        super().__init__(message)
        self.retryable = retryable
