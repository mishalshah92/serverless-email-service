from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "websites"

PRESETS: dict[str, dict[str, str]] = {
    "contact": {
        "subject": "Contact from ${name}",
        "text_body": "Name: ${name}\nEmail: ${email}\nMessage:\n${message}",
        "html_body": (
            "<h1>Contact form</h1>"
            "<p><strong>Name:</strong> ${name}</p>"
            "<p><strong>Email:</strong> ${email}</p>"
            "<p>${message}</p>"
        ),
    },
    "booking": {
        "subject": "Booking enquiry from ${name}",
        "text_body": (
            "Name: ${name}\nEmail: ${email}\nCheck-in: ${check_in}\n"
            "Check-out: ${check_out}\nGuests: ${guests}\nNotes:\n${notes}"
        ),
        "html_body": (
            "<h1>Booking enquiry</h1>"
            "<p>${name}</p><p>${email}</p>"
            "<p>${check_in} to ${check_out}</p>"
            "<p>Guests: ${guests}</p><p>${notes}</p>"
        ),
    },
    "quote": {
        "subject": "Quote request from ${name}",
        "text_body": "Name: ${name}\nEmail: ${email}\nProject:\n${message}",
        "html_body": (
            "<h1>Quote request</h1>"
            "<p><strong>Name:</strong> ${name}</p>"
            "<p><strong>Email:</strong> ${email}</p>"
            "<p>${message}</p>"
        ),
    },
    "blank": {
        "subject": "Website form submission",
        "text_body": "Request ID: ${request_id}",
        "html_body": "<p>Request ID: ${request_id}</p>",
    },
}


def main() -> None:
    args = _parse_args()
    output = CONFIG / args.website / "templates" / f"{args.template_id}.json"
    if output.exists() and not args.force:
        raise SystemExit(f"refusing to overwrite existing template: {output}")

    preset = PRESETS[args.preset]
    template = {
        "template_id": args.template_id,
        "version": args.version,
        "subject": args.subject or preset["subject"],
        "text_body": args.text_body or preset["text_body"],
        "html_body": args.html_body or preset["html_body"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(template, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"created {output}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an email template for a website.")
    parser.add_argument("--website", required=True)
    parser.add_argument("--template-id", required=True)
    parser.add_argument("--version", default="v1")
    parser.add_argument("--preset", choices=sorted(PRESETS), default="contact")
    parser.add_argument("--subject", default="")
    parser.add_argument("--text-body", default="")
    parser.add_argument("--html-body", default="")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing template.")
    return parser.parse_args()


if __name__ == "__main__":
    main()
