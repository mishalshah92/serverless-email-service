resource "aws_ssm_parameter" "turnstile_secret" {
  count = local.create_turnstile_widget ? 1 : 0

  name  = var.turnstile_secret_parameter_name
  type  = "SecureString"
  value = cloudflare_turnstile_widget.main[0].secret
  tags  = var.tags
}
