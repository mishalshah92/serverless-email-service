from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    _check_python()
    _check_tool("terraform", required=not args.skip_terraform_check)
    if not args.skip_install:
        _run([sys.executable, "-m", "pip", "install", "-e", ".[dev]"])
    if not args.skip_checks:
        _run([sys.executable, "-m", "ruff", "check", "."])
        _run([sys.executable, "-m", "mypy"])
        _run([sys.executable, "-m", "pytest"])
    _run([sys.executable, "scripts/build_lambda.py"])
    print("setup complete")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare the local development workspace.")
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Do not install dev dependencies.",
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Do not run lint, typecheck, and tests.",
    )
    parser.add_argument(
        "--skip-terraform-check",
        action="store_true",
        help="Do not require Terraform to be available on PATH.",
    )
    return parser.parse_args()


def _check_python() -> None:
    print(f"python ok: {sys.version.split()[0]}")


def _check_tool(name: str, *, required: bool) -> None:
    path = shutil.which(name)
    if path:
        print(f"{name} ok: {path}")
        return
    message = f"{name} was not found on PATH."
    if required:
        raise SystemExit(message)
    print(f"warning: {message}")


def _run(command: list[str]) -> None:
    print("+ " + " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
