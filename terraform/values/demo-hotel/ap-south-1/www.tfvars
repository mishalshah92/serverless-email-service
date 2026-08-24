project_name                    = "static-website-email-service"
website_name                    = "demo-hotel"
subdomain                       = "www"
aws_region                      = "ap-south-1"
log_retention_days              = 14
turnstile_secret_parameter_name = "/static-website-email-service/demo-hotel/www/turnstile/secret"
turnstile_widget_enabled        = false
turnstile_widget_domain         = "www.demo.example"
turnstile_widget_mode           = "managed"

tags = {
  project   = "static-website-email-service"
  website   = "demo-hotel"
  subdomain = "www"
}
