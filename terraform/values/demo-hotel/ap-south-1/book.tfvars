project_name                    = "static-website-email-service"
website_name                    = "demo-hotel"
subdomain                       = "book"
aws_region                      = "ap-south-1"
log_retention_days              = 30
turnstile_secret_parameter_name = "/static-website-email-service/demo-hotel/book/turnstile/secret"
turnstile_widget_enabled        = false
turnstile_widget_domain         = "book.demo.example"
turnstile_widget_mode           = "managed"

tags = {
  project   = "static-website-email-service"
  website   = "demo-hotel"
  subdomain = "book"
}
