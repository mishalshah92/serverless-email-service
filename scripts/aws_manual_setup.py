from __future__ import annotations

import argparse
import getpass
import subprocess


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run AWS setup tasks that are intentionally manual."
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    state = subcommands.add_parser("state", help="Create Terraform state bucket and lock table.")
    state.add_argument("--bucket", required=True)
    state.add_argument("--table", required=True)
    state.add_argument("--region", required=True)
    state.add_argument(
        "--apply",
        action="store_true",
        help="Run commands. Without this, only print them.",
    )

    turnstile = subcommands.add_parser("turnstile-secret", help="Store a Turnstile secret in SSM.")
    turnstile.add_argument("--name", required=True, help="SSM parameter name.")
    turnstile.add_argument("--region", required=True)
    turnstile.add_argument(
        "--value-env",
        help="Read the secret value from this environment variable.",
    )

    smtp = subcommands.add_parser("smtp-provider", help="Store SMTP provider settings in SSM.")
    smtp.add_argument("--prefix", required=True, help="SSM prefix ending with the provider ID.")
    smtp.add_argument("--region", required=True)
    smtp.add_argument("--host", required=True)
    smtp.add_argument("--port", default="587")
    smtp.add_argument("--username", required=True)
    smtp.add_argument("--security", default="starttls", choices=("starttls", "ssl", "none"))
    smtp.add_argument(
        "--password-env",
        help="Read the SMTP password from this environment variable.",
    )

    ses = subcommands.add_parser("ses-identity", help="Create an SES email identity.")
    ses.add_argument("--identity", required=True, help="Email address or domain.")
    ses.add_argument("--region", required=True)

    args = parser.parse_args()
    if args.command == "state":
        _state(args)
    elif args.command == "turnstile-secret":
        _turnstile_secret(args)
    elif args.command == "smtp-provider":
        _smtp_provider(args)
    elif args.command == "ses-identity":
        _ses_identity(args)


def _state(args: argparse.Namespace) -> None:
    commands = [
        [
            "aws",
            "s3api",
            "create-bucket",
            "--bucket",
            args.bucket,
            "--region",
            args.region,
            "--create-bucket-configuration",
            f"LocationConstraint={args.region}",
        ],
        [
            "aws",
            "s3api",
            "put-bucket-versioning",
            "--bucket",
            args.bucket,
            "--versioning-configuration",
            "Status=Enabled",
        ],
        [
            "aws",
            "s3api",
            "put-bucket-encryption",
            "--bucket",
            args.bucket,
            "--server-side-encryption-configuration",
            '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}',
        ],
        [
            "aws",
            "dynamodb",
            "create-table",
            "--table-name",
            args.table,
            "--attribute-definitions",
            "AttributeName=LockID,AttributeType=S",
            "--key-schema",
            "AttributeName=LockID,KeyType=HASH",
            "--billing-mode",
            "PAY_PER_REQUEST",
            "--region",
            args.region,
        ],
    ]
    for command in commands:
        _run_or_print(command, apply=args.apply)


def _turnstile_secret(args: argparse.Namespace) -> None:
    value = _secret(args.value_env, "Turnstile secret")
    _put_parameter(args.name, "SecureString", value, args.region)


def _smtp_provider(args: argparse.Namespace) -> None:
    password = _secret(args.password_env, "SMTP password")
    values = {
        "host": ("String", args.host),
        "port": ("String", args.port),
        "username": ("SecureString", args.username),
        "password": ("SecureString", password),
        "security": ("String", args.security),
    }
    for name, (parameter_type, value) in values.items():
        _put_parameter(f"{args.prefix.rstrip('/')}/{name}", parameter_type, value, args.region)


def _ses_identity(args: argparse.Namespace) -> None:
    command = [
        "aws",
        "sesv2",
        "create-email-identity",
        "--email-identity",
        args.identity,
        "--region",
        args.region,
    ]
    _run_or_print(command, apply=True)


def _secret(env_name: str | None, prompt: str) -> str:
    if env_name:
        import os

        value = os.environ.get(env_name)
        if not value:
            raise SystemExit(f"environment variable is empty or missing: {env_name}")
        return value
    return getpass.getpass(f"{prompt}: ")


def _put_parameter(name: str, parameter_type: str, value: str, region: str) -> None:
    command = [
        "aws",
        "ssm",
        "put-parameter",
        "--name",
        name,
        "--type",
        parameter_type,
        "--value",
        value,
        "--overwrite",
        "--region",
        region,
    ]
    print(
        "+ aws ssm put-parameter "
        f"--name {name} --type {parameter_type} --overwrite --region {region}"
    )
    subprocess.run(command, check=True)


def _run_or_print(command: list[str], *, apply: bool) -> None:
    print("+ " + " ".join(command))
    if apply:
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
