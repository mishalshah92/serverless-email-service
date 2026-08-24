# 0002 Use Terraform

Status: Accepted

## Context

Infrastructure should be repeatable and match the reference repository's conventions.

## Decision

Use Terraform under `terraform/`, with reusable modules and website/region/deployment-specific tfvars and backend config files.

## Consequences

Deployments are reviewable through plans. State must be remote and must never be committed.
