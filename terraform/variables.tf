variable "project_name" {
  type    = string
  default = "static-website-email-service"
}

variable "website_name" {
  type = string
}

variable "deployment_name" {
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

variable "tags" {
  type    = map(string)
  default = {}
}
