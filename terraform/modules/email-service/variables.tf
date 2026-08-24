variable "project_name" {
  description = "Project name used in AWS resource names."
  type        = string
}

variable "website_name" {
  description = "Website name used in AWS resource names."
  type        = string
}

variable "subdomain" {
  description = "Subdomain used in AWS resource names."
  type        = string
}

variable "lambda_package_path" {
  description = "Path to the Lambda zip package."
  type        = string
}

variable "aws_region" {
  description = "AWS region."
  type        = string
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days."
  type        = number
  default     = 14
}

variable "turnstile_secret_parameter_name" {
  description = "SSM SecureString parameter name containing the Turnstile secret."
  type        = string
  default     = ""
}

variable "turnstile_widget_enabled" {
  description = "Create a Cloudflare Turnstile widget and store its secret in SSM."
  type        = bool
  default     = false
}

variable "turnstile_widget_domain" {
  description = "Public hostname allowed to use the Turnstile widget for this subdomain deployment."
  type        = string
  default     = ""
}

variable "turnstile_widget_mode" {
  description = "Turnstile widget mode."
  type        = string
  default     = "managed"
}

variable "cloudflare_account_id" {
  description = "Cloudflare account ID used when creating Turnstile widgets."
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags applied to AWS resources."
  type        = map(string)
  default     = {}
}
