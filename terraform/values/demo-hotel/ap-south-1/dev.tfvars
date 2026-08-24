project_name                    = "static-website-email-service"
website_name                    = "demo-hotel"
deployment_name                 = "dev"
aws_region                      = "ap-south-1"
log_retention_days              = 14
turnstile_secret_parameter_name = "/static-website-email-service/dev/turnstile/secret"

tags = {
  project    = "static-website-email-service"
  website    = "demo-hotel"
  deployment = "dev"
}
