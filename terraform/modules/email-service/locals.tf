locals {
  name = "${var.project_name}-${var.website_name}-${var.subdomain}"
  create_turnstile_widget = (
    var.turnstile_widget_enabled &&
    var.cloudflare_account_id != "" &&
    var.turnstile_secret_parameter_name != "" &&
    var.turnstile_widget_domain != ""
  )
}
