from __future__ import annotations

import base64
import dataclasses
import hmac
import json
import time
from hashlib import sha256


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _split_key(admin_api_key: str) -> tuple[str, bytes]:
    kid, secret_hex = admin_api_key.split(":", 1)
    kid = kid.strip()
    secret_hex = secret_hex.strip()
    if not kid or not secret_hex:
        raise RuntimeError("Invalid GHOST_ADMIN_API_KEY (expected id:secret)")
    try:
        secret = bytes.fromhex(secret_hex)
    except Exception as e:
        raise RuntimeError("Invalid GHOST_ADMIN_API_KEY secret (expected hex)") from e
    return kid, secret


def generate_admin_jwt(
    admin_api_key: str,
    *,
    now_s: int | None = None,
    ttl_s: int = 300,
) -> tuple[str, int]:
    """
    Generates a Ghost Admin API JWT.

    - HS256
    - header.kid: id part of API key
    - payload.aud: "/admin/"
    - exp <= now + 5 minutes
    """
    if now_s is None:
        now_s = int(time.time())
    if ttl_s <= 0 or ttl_s > 300:
        raise RuntimeError("ttl_s must be between 1 and 300 seconds")

    kid, secret = _split_key(admin_api_key)

    header = {"alg": "HS256", "typ": "JWT", "kid": kid}
    exp_s = now_s + ttl_s
    payload = {"iat": now_s, "exp": exp_s, "aud": "/admin/"}

    header_b64 = _b64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    sig = hmac.new(secret, signing_input, sha256).digest()
    token = f"{header_b64}.{payload_b64}.{_b64url(sig)}"
    return token, exp_s


@dataclasses.dataclass
class JwtCache:
    token: str | None = None
    exp_s: int | None = None

    def get_valid(self, *, now_s: int | None = None, skew_s: int = 15) -> str | None:
        if now_s is None:
            now_s = int(time.time())
        if not self.token or not self.exp_s:
            return None
        if now_s + skew_s >= self.exp_s:
            return None
        return self.token

    def set(self, token: str, exp_s: int) -> None:
        self.token = token
        self.exp_s = exp_s
