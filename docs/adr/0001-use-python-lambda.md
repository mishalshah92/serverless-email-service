# 0001 Use Python on AWS Lambda

Status: Accepted

## Context

The service is request/queue driven and should have minimal idle cost.

## Decision

Use Python on AWS Lambda with framework-light handlers.

## Consequences

Packaging stays small, Lambda can scale to zero, and boto3 is available in the Lambda runtime. Local tests avoid AWS calls through dependency injection.
