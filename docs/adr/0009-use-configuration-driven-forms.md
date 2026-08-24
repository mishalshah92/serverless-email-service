# 0009 Use Configuration-Driven Forms

Status: Accepted

## Context

The service must support many sites and forms without new Lambda deployments per form.

## Decision

Forms are described by backend configuration and validated dynamically.

## Consequences

New forms can be added through configuration. Validation code must be strict and well tested.
