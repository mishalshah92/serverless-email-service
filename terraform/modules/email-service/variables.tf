variable "project_name" {
  description = "Project name used in AWS resource names."
  type        = string
}

variable "website_name" {
  description = "Website name used in AWS resource names."
  type        = string
}

variable "deployment_name" {
  description = "Deployment name used in AWS resource names."
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

variable "tags" {
  description = "Tags applied to AWS resources."
  type        = map(string)
  default     = {}
}
