resource "cloudflare_turnstile_widget" "main" {
  count = local.create_turnstile_widget ? 1 : 0

  account_id = var.cloudflare_account_id
  name       = local.name
  domains    = [var.turnstile_widget_domain]
  mode       = var.turnstile_widget_mode
  region     = "world"
}
