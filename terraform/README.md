# Terraform

Terraform code will live here.

The layout follows the compact module-oriented style from the reference repository. A single root module is reused for every website, region, and subdomain. Values are organized by website first.

```text
terraform/
|- values/
|  `- demo-hotel/
|     `- ap-south-1/
|        |- book.backend.hcl
|        |- book.tfvars
|        |- www.backend.hcl
|        `- www.tfvars
`- modules/
```

Initialize the `www` subdomain with:

```sh
terraform init -backend-config=values/demo-hotel/ap-south-1/www.backend.hcl
terraform plan -var-file=values/demo-hotel/ap-south-1/www.tfvars
```

Use the matching subdomain files for each website deployment after reviewing the plan.

## Turnstile

Terraform can optionally create a Cloudflare Turnstile widget and store the generated secret in AWS SSM Parameter Store.

Enable it in a website tfvars file:

```hcl
cloudflare_account_id    = "your-cloudflare-account-id"
turnstile_widget_enabled = true
turnstile_widget_domain  = "www.example.com"
```

Supply the Cloudflare API token outside Git:

```sh
export TF_VAR_cloudflare_api_token="..."
```

The Turnstile secret will be written to the configured SSM SecureString parameter and will also be present in Terraform state.
