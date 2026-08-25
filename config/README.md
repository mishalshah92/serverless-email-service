# Configuration

Repository-managed website configuration lives here. These files are safe to commit when they contain only non-secret values.

```text
config/
`- websites/
   `- {website}/
      `- templates/
         `- {template_id}.json
```

Templates use Python `string.Template` placeholders such as `${name}` and `${email}`. The public frontend must not choose a template. Form configuration chooses the trusted `template_id`; Terraform will later publish these files into DynamoDB as `TENANT#{tenant_id}` / `TEMPLATE#{template_id}` items.
