output "api_endpoint" {
  value = module.email_service.api_endpoint
}

output "table_name" {
  value = module.email_service.table_name
}

output "turnstile_sitekey" {
  description = "Public Turnstile sitekey for the static frontend."
  value       = module.email_service.turnstile_sitekey
}
