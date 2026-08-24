from __future__ import annotations

import json
from urllib import parse, request


class DisabledTurnstileVerifier:
    def verify(self, token: str, remote_ip: str | None, expected_hostname: str | None) -> bool:
        return True


class CloudflareTurnstileVerifier:
    verify_url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

    def __init__(self, secret: str) -> None:
        self._secret = secret

    def verify(self, token: str, remote_ip: str | None, expected_hostname: str | None) -> bool:
        data = {"secret": self._secret, "response": token}
        if remote_ip:
            data["remoteip"] = remote_ip
        req = request.Request(self.verify_url, data=parse.urlencode(data).encode(), method="POST")
        with request.urlopen(req, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not payload.get("success"):
            return False
        return not expected_hostname or payload.get("hostname") == expected_hostname
