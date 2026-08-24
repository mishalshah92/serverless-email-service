# 0007 Treat Static Frontends as Untrusted

Status: Accepted

## Context

Static JavaScript is public and can be copied or modified.

## Decision

The frontend cannot control recipients, senders, provider credentials, template IDs, SES identity, or arbitrary subject.

## Consequences

Trusted delivery settings come only from backend configuration.
