project_name                    = "static-website-email-service"
website_name                    = "demo-hotel"
deployment_name                 = "prod"
aws_region                      = "ap-south-1"
log_retention_days              = 30
turnstile_secret_parameter_name = "/static-website-email-service/prod/turnstile/secret"

tags = {
  project    = "static-website-email-service"
  website    = "demo-hotel"
  deployment = "prod"
}
