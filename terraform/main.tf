module "email_service" {
  source = "./modules/email-service"

  project_name                    = var.project_name
  website_name                    = var.website_name
  deployment_name                 = var.deployment_name
  aws_region                      = var.aws_region
  lambda_package_path             = var.lambda_package_path
  log_retention_days              = var.log_retention_days
  turnstile_secret_parameter_name = var.turnstile_secret_parameter_name
  tags                            = var.tags
}
