# Operations Runbook

Use request IDs, SQS message IDs, and provider message IDs when investigating.

## Delivery Failures

1. Check the worker Lambda logs for `request_id`.
2. Check SQS DLQ visible message count.
3. Verify provider configuration in DynamoDB.
4. Verify SES identity or SMTP credentials.

## DLQ Messages

Inspect one message body without exposing it in shared channels:

```sh
aws sqs receive-message --queue-url "$DLQ_URL" --max-number-of-messages 1
```

Fix the root cause, then redrive from the DLQ using the AWS console or CLI.

## Bounce or Complaint Spike

Pause the affected form or provider, inspect SES event records, and verify list quality. Do not keep sending to hard-bounced or complaining recipients.

## SMTP Credentials Rejected

Rotate credentials in SSM SecureString parameters. Do not store credentials in Terraform variables or DynamoDB plaintext.

## Turnstile Outage

Temporarily disabling Turnstile should be a conscious environment/configuration change and should be paired with stricter quotas.

## High Traffic or Spam

Lower quotas for the affected site/form, check source IP patterns, and consider adding WAF only if abuse cannot be controlled more cheaply.
