# 0010 Minimize PII Retention

Status: Accepted

## Context

Form submissions may contain personal data.

## Decision

Store operational metadata by default and avoid logging full payloads or email bodies.

## Consequences

Troubleshooting may need correlation IDs and provider message IDs rather than raw form content.
