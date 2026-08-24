# Setup

This service can keep most non-secret configuration in the repository and let Terraform populate AWS. Do not store real secrets in Git.

## What Terraform Should Manage

Safe to store in repo:

- tenants
- sites
- forms
- allowed origins
- field definitions
- recipients
- senders
- template IDs
- provider IDs
- email templates
- SES provider configuration
- SSM parameter names

Do not store in repo:

- SMTP passwords
- Gmail app passwords
- Turnstile secret
- private provider credentials

## First-Time AWS Prerequisites

Create or confirm:

- Terraform remote state S3 bucket
- Terraform lock DynamoDB table
- SES verified domain or email identity
- SES DKIM/SPF/DMARC DNS records
- Cloudflare Turnstile site
- SSM SecureString parameters for secrets

## Website Values

Values are organized by website, region, and deployment:

```text
terraform/values/{website}/{region}/{deployment-name}.tfvars
```

Current examples:

```text
terraform/values/demo-hotel/ap-south-1/dev.tfvars
terraform/values/demo-hotel/ap-south-1/prod.tfvars
```

Store non-secret values only.

Use `website_name` and `deployment_name` inside each tfvars file. For example, `terraform/values/demo-hotel/ap-south-1/dev.tfvars` sets:

```hcl
website_name    = "demo-hotel"
deployment_name = "dev"
```

## Secret Parameters

Create the Turnstile secret:

```sh
aws ssm put-parameter \
  --name "/static-website-email-service/dev/turnstile/secret" \
  --type SecureString \
  --value "replace-with-real-secret" \
  --overwrite
```

For SMTP:

```sh
aws ssm put-parameter --name "/static-website-email-service/dev/providers/demo-hotel/primary-smtp/host" --type String --value "smtp.gmail.com" --overwrite
aws ssm put-parameter --name "/static-website-email-service/dev/providers/demo-hotel/primary-smtp/port" --type String --value "587" --overwrite
aws ssm put-parameter --name "/static-website-email-service/dev/providers/demo-hotel/primary-smtp/username" --type SecureString --value "website@example.com" --overwrite
aws ssm put-parameter --name "/static-website-email-service/dev/providers/demo-hotel/primary-smtp/password" --type SecureString --value "replace-with-real-password" --overwrite
aws ssm put-parameter --name "/static-website-email-service/dev/providers/demo-hotel/primary-smtp/security" --type String --value "starttls" --overwrite
```

## Terraform Commands

Build the Lambda package first:

```sh
make build
```

Initialize dev:

```sh
cd terraform
terraform init -backend-config=values/demo-hotel/ap-south-1/dev.backend.hcl
```

Plan dev:

```sh
terraform plan -var-file=values/demo-hotel/ap-south-1/dev.tfvars
```

Apply only after reviewing the plan:

```sh
terraform apply -var-file=values/demo-hotel/ap-south-1/dev.tfvars
```

## Backend Configuration

Backend config lives in:

```text
terraform/values/demo-hotel/ap-south-1/dev.backend.hcl
terraform/values/demo-hotel/ap-south-1/prod.backend.hcl
```

Environment values live in:

```text
terraform/values/demo-hotel/ap-south-1/dev.tfvars
terraform/values/demo-hotel/ap-south-1/prod.tfvars
```

Only commit `terraform/values/**/*.tfvars` when they contain non-secret values.

## Form Configuration

The current example tenant config is:

```text
examples/demo-tenant.json
```

The intended next step is for Terraform to populate DynamoDB items from repo-managed, non-secret config. Secrets should remain SSM parameter values only.

## Frontend Values

The static website can safely know:

- API URL
- public site ID
- form ID
- Turnstile public site key

The static website must not know:

- recipient
- sender
- provider credentials
- SMTP password
- SES identity
- template ID
- Turnstile secret
