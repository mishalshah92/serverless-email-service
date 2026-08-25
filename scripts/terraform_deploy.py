from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TERRAFORM = ROOT / "terraform"


def main() -> None:
    args = _parse_args()
    values = Path("values") / args.website / args.region / f"{args.subdomain}.tfvars"
    backend = Path("values") / args.website / args.region / f"{args.subdomain}.backend.hcl"
    _require(TERRAFORM / values)
    _require(TERRAFORM / backend)

    _run(["terraform", "init", f"-backend-config={backend.as_posix()}"])
    command = [
        "terraform",
        args.action,
        "-var",
        f"website_name={args.website}",
        "-var",
        f"aws_region={args.region}",
        "-var",
        f"subdomain={args.subdomain}",
        "-var-file",
        values.as_posix(),
    ]
    if args.action == "plan":
        command.extend(["-out", args.out])
    _run(command)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Terraform for a website subdomain deployment."
    )
    parser.add_argument("action", choices=("plan", "apply"))
    parser.add_argument("--website", default="demo-hotel")
    parser.add_argument("--region", default="ap-south-1")
    parser.add_argument("--subdomain", default="www")
    parser.add_argument("--out", default="tfplan", help="Plan output path used for plan actions.")
    return parser.parse_args()


def _require(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"required file not found: {path}")


def _run(command: list[str]) -> None:
    print("+ " + " ".join(command))
    subprocess.run(command, cwd=TERRAFORM, check=True)


if __name__ == "__main__":
    main()
