# 0006 Use SES/SMTP Provider Abstraction

Status: Accepted

## Context

SES is preferred, but some tenants may need Gmail or custom SMTP.

## Decision

Core code depends on a `MailProvider` protocol. SES and SMTP are adapters.

## Consequences

Provider-specific details stay out of validation, templates, and handlers.
