# 0004 Use SQS for Asynchronous Delivery

Status: Accepted

## Context

Email providers can be slow or transiently unavailable.

## Decision

The intake Lambda queues validated jobs to SQS. A worker Lambda sends email later.

## Consequences

Users receive fast `202 Accepted` responses, retries are reliable, and DLQ handling is available.
