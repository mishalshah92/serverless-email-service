module "email_service" {
  source = "./modules/email-service"

  project_name                    = var.project_name
  website_name                    = var.website_name
  subdomain                       = var.subdomain
  aws_region                      = var.aws_region
  lambda_package_path             = var.lambda_package_path
  log_retention_days              = var.log_retention_days
  turnstile_secret_parameter_name = var.turnstile_secret_parameter_name
  turnstile_widget_enabled        = var.turnstile_widget_enabled
  turnstile_widget_domain         = var.turnstile_widget_domain
  turnstile_widget_mode           = var.turnstile_widget_mode
  cloudflare_account_id           = var.cloudflare_account_id
  tags                            = var.tags
}
