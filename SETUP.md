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
- Cloudflare API token if Terraform will create the Turnstile widget
- SSM SecureString parameters for SMTP secrets

## Website Values

Values are organized by website, region, and subdomain:

```text
terraform/values/{website}/{region}/{subdomain}.tfvars
```

Current examples:

```text
terraform/values/demo-hotel/ap-south-1/www.tfvars
terraform/values/demo-hotel/ap-south-1/book.tfvars
```

Store non-secret values only.

The path and Makefile parameters are the source of truth for `website_name`, `aws_region`, and `subdomain`. Do not repeat them in the tfvars file. For example:

```sh
make terraform-plan WEBSITE=demo-hotel REGION=ap-south-1 SUBDOMAIN=www
```

passes `website_name`, `aws_region`, and `subdomain` to Terraform as inline variables.

## Secret Parameters

## Turnstile

Terraform can create the Cloudflare Turnstile widget and write its generated secret into AWS SSM.

Set these non-secret values in the website tfvars file:

```hcl
cloudflare_account_id    = "your-cloudflare-account-id"
turnstile_widget_enabled = true
turnstile_widget_domain  = "www.example.com"
turnstile_widget_mode    = "managed"
```

Supply the Cloudflare API token outside the repo:

```sh
export TF_VAR_cloudflare_api_token="replace-with-cloudflare-token"
```

The token needs Cloudflare Turnstile edit permissions. Terraform will store the generated secret in:

```text
turnstile_secret_parameter_name
```

Important: the Turnstile secret will also exist in Terraform state because Terraform receives it from Cloudflare before writing it to SSM. Keep remote state encrypted and tightly access-controlled.

If you do not want Terraform to manage Turnstile, create the SSM secret manually:

```sh
aws ssm put-parameter \
  --name "/static-website-email-service/demo-hotel/www/turnstile/secret" \
  --type SecureString \
  --value "replace-with-real-secret" \
  --overwrite
```

For SMTP:

```sh
aws ssm put-parameter --name "/static-website-email-service/demo-hotel/www/providers/primary-smtp/host" --type String --value "smtp.gmail.com" --overwrite
aws ssm put-parameter --name "/static-website-email-service/demo-hotel/www/providers/primary-smtp/port" --type String --value "587" --overwrite
aws ssm put-parameter --name "/static-website-email-service/demo-hotel/www/providers/primary-smtp/username" --type SecureString --value "website@example.com" --overwrite
aws ssm put-parameter --name "/static-website-email-service/demo-hotel/www/providers/primary-smtp/password" --type SecureString --value "replace-with-real-password" --overwrite
aws ssm put-parameter --name "/static-website-email-service/demo-hotel/www/providers/primary-smtp/security" --type String --value "starttls" --overwrite
```

## Terraform Commands

Build the Lambda package first:

```sh
make build
```

The easiest path is the Makefile, which derives the tfvars and backend config paths and passes `website_name`, `aws_region`, and `subdomain` inline:

```sh
make terraform-plan WEBSITE=demo-hotel REGION=ap-south-1 SUBDOMAIN=www
make terraform-apply WEBSITE=demo-hotel REGION=ap-south-1 SUBDOMAIN=www
```

Or run Terraform directly:

```sh
cd terraform
terraform init -backend-config=values/demo-hotel/ap-south-1/www.backend.hcl
```

Plan:

```sh
terraform plan \
  -var website_name=demo-hotel \
  -var aws_region=ap-south-1 \
  -var subdomain=www \
  -var-file values/demo-hotel/ap-south-1/www.tfvars
```

Apply only after reviewing the plan:

```sh
terraform apply \
  -var website_name=demo-hotel \
  -var aws_region=ap-south-1 \
  -var subdomain=www \
  -var-file values/demo-hotel/ap-south-1/www.tfvars
```

## Backend Configuration

Backend config lives in:

```text
terraform/values/demo-hotel/ap-south-1/www.backend.hcl
terraform/values/demo-hotel/ap-south-1/book.backend.hcl
```

Website values live in:

```text
terraform/values/demo-hotel/ap-south-1/www.tfvars
terraform/values/demo-hotel/ap-south-1/book.tfvars
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
