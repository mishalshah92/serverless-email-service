locals {
  common_tags = merge(
    {
      project   = var.project_name
      website   = var.website_name
      subdomain = var.subdomain
    },
    var.tags
  )
}
