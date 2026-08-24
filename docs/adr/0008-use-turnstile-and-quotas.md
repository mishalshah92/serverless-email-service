# 0008 Use Turnstile and Quotas

Status: Accepted

## Context

Browser API secrets are not secret.

## Decision

Use server-side Cloudflare Turnstile verification, allowed-origin signals, honeypots, and quotas.

## Consequences

Abuse protection is defense in depth. Origin checks are not treated as authentication.
