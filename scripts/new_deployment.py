from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALUES = ROOT / "terraform" / "values"


def main() -> None:
    args = _parse_args()
    directory = VALUES / args.website / args.region
    tfvars = directory / f"{args.subdomain}.tfvars"
    backend = directory / f"{args.subdomain}.backend.hcl"

    if not args.force:
        _refuse_existing(tfvars)
        _refuse_existing(backend)

    directory.mkdir(parents=True, exist_ok=True)
    tfvars.write_text(_tfvars(args), encoding="utf-8")
    backend.write_text(_backend(args), encoding="utf-8")
    print(f"created {tfvars}")
    print(f"created {backend}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create Terraform values files for a website subdomain."
    )
    parser.add_argument("--website", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--subdomain", required=True)
    parser.add_argument("--state-bucket", required=True)
    parser.add_argument("--state-table", required=True)
    parser.add_argument("--project-name", default="static-website-email-service")
    parser.add_argument("--log-retention-days", default="14")
    parser.add_argument("--turnstile-domain", default="")
    parser.add_argument("--turnstile-enabled", action="store_true")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    return parser.parse_args()


def _refuse_existing(path: Path) -> None:
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing file: {path}")


def _tfvars(args: argparse.Namespace) -> str:
    domain = args.turnstile_domain or f"{args.subdomain}.{args.website}.example"
    enabled = str(bool(args.turnstile_enabled)).lower()
    secret_name = f"/{args.project_name}/{args.website}/{args.subdomain}/turnstile/secret"
    return (
        f'project_name                    = "{args.project_name}"\n'
        f"log_retention_days              = {args.log_retention_days}\n"
        f'turnstile_secret_parameter_name = "{secret_name}"\n'
        f"turnstile_widget_enabled        = {enabled}\n"
        f'turnstile_widget_domain         = "{domain}"\n'
        'turnstile_widget_mode           = "managed"\n'
    )


def _backend(args: argparse.Namespace) -> str:
    key = (
        f"mishalshah92/{args.project_name}/{args.website}/"
        f"{args.region}/{args.subdomain}/tfstate"
    )
    return (
        f'region         = "{args.region}"\n'
        f'bucket         = "{args.state_bucket}"\n'
        f'dynamodb_table = "{args.state_table}"\n'
        "encrypt        = true\n"
        f'key            = "{key}"\n'
    )


if __name__ == "__main__":
    main()
