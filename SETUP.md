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

## Local Developer Setup

Run the initial local setup:

```sh
python scripts/setup.py
```

This installs dev dependencies, runs checks, and builds the Lambda package. To skip dependency installation:

```sh
python scripts/setup.py --skip-install
```

The Makefile wraps the same script:

```sh
make setup
```

## Terraform State Bootstrap

Create the remote Terraform state bucket and lock table with the AWS helper. The first command is a dry run and only prints AWS CLI commands:

```sh
python scripts/aws_manual_setup.py state \
  --bucket ms92-tf-states \
  --table ms92-tf-states \
  --region ap-south-1
```

Run it for real only after reviewing the printed commands:

```sh
python scripts/aws_manual_setup.py state \
  --bucket ms92-tf-states \
  --table ms92-tf-states \
  --region ap-south-1 \
  --apply
```

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

Create a new values/backend pair with:

```sh
python scripts/new_deployment.py \
  --website demo-hotel \
  --region ap-south-1 \
  --subdomain contact \
  --state-bucket ms92-tf-states \
  --state-table ms92-tf-states
```

The Makefile wrapper is:

```sh
make new-deployment WEBSITE=demo-hotel REGION=ap-south-1 SUBDOMAIN=contact
```

## Secret Parameters

## Email Templates

Store source-controlled templates here:

```text
config/websites/{website}/templates/{template_id}.json
```

Create one with:

```sh
python scripts/new_template.py \
  --website demo-hotel \
  --template-id quote-v1 \
  --preset quote
```

The Makefile wrapper is:

```sh
make new-template WEBSITE=demo-hotel TEMPLATE_ID=quote-v1 TEMPLATE_PRESET=quote
```

Each file contains:

```json
{
  "template_id": "quote-v1",
  "version": "v1",
  "subject": "Quote request from ${name}",
  "text_body": "Name: ${name}\nEmail: ${email}\nProject:\n${message}",
  "html_body": "<h1>Quote request</h1><p>${name}</p><p>${email}</p><p>${message}</p>"
}
```

The API does not select templates directly. A trusted form config maps the API call to a template:

```text
POST /v1/forms/contact -> FORM#contact -> template_id contact-v1
```

Terraform will later publish these JSON files into DynamoDB as:

```text
pk = TENANT#{tenant_id}
sk = TEMPLATE#{template_id}
```

## SES Identity

Create an SES identity with:

```sh
python scripts/aws_manual_setup.py ses-identity \
  --identity example.com \
  --region ap-south-1
```

For domain identities, SES still returns DNS records that must be added wherever DNS is hosted.

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
python scripts/aws_manual_setup.py turnstile-secret \
  --name "/static-website-email-service/demo-hotel/www/turnstile/secret" \
  --region ap-south-1
```

For SMTP:

```sh
python scripts/aws_manual_setup.py smtp-provider \
  --prefix "/static-website-email-service/demo-hotel/www/providers/primary-smtp" \
  --region ap-south-1 \
  --host smtp.gmail.com \
  --port 587 \
  --username website@example.com \
  --security starttls
```

The scripts prompt for secret values so passwords are not stored in shell history. For CI or one-off automation, pass `--value-env` or `--password-env` and provide the secret through an environment variable.

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

The direct Python wrapper is:

```sh
python scripts/terraform_deploy.py plan --website demo-hotel --region ap-south-1 --subdomain www
python scripts/terraform_deploy.py apply --website demo-hotel --region ap-south-1 --subdomain www
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
