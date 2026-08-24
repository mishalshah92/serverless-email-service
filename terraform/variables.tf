variable "project_name" {
  type    = string
  default = "static-website-email-service"
}

variable "website_name" {
  type = string
}

variable "subdomain" {
  type = string
}

variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

variable "lambda_package_path" {
  type    = string
  default = "../build/email_service.zip"
}

variable "log_retention_days" {
  type    = number
  default = 14
}

variable "turnstile_secret_parameter_name" {
  type    = string
  default = ""
}

variable "cloudflare_api_token" {
  description = "Cloudflare API token with Turnstile edit permissions. Supply via TF_VAR_cloudflare_api_token."
  type        = string
  default     = ""
  sensitive   = true
}

variable "cloudflare_account_id" {
  description = "Cloudflare account ID used when creating Turnstile widgets."
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

  validation {
    condition     = contains(["managed", "non-interactive", "invisible"], var.turnstile_widget_mode)
    error_message = "Turnstile widget mode must be managed, non-interactive, or invisible."
  }
}

variable "tags" {
  type    = map(string)
  default = {}
}
