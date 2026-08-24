# 0005 Use DynamoDB

Status: Accepted

## Context

The service needs low-cost configuration and status storage with simple key-value access patterns.

## Decision

Use DynamoDB instead of a relational database.

## Consequences

No fixed database server cost. Data access must be designed around keys and avoid scans.
