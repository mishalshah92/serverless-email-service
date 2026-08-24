# Terraform

Terraform code will live here.

The layout follows the compact module-oriented style from the reference repository. A single root module is reused for every website, region, and deployment. Values are organized by website first.

```text
terraform/
|- values/
|  `- demo-hotel/
|     `- ap-south-1/
|        |- dev.backend.hcl
|        |- dev.tfvars
|        |- prod.backend.hcl
|        `- prod.tfvars
`- modules/
```

Initialize dev with:

```sh
terraform init -backend-config=values/demo-hotel/ap-south-1/dev.backend.hcl
terraform plan -var-file=values/demo-hotel/ap-south-1/dev.tfvars
```

Use the prod files for production after reviewing the plan.
