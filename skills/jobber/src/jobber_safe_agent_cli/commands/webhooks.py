from __future__ import annotations

import base64
import hashlib
import hmac
from pathlib import Path
from typing import Any

from ..errors import ValidationError
from ..schema_registry import webhook_topics


def cmd_webhooks_topics(args, ctx) -> int:
    _ = args
    topics = webhook_topics()
    out = {
        "ok": True,
        "command": "webhooks.topics",
        "count": len(topics),
        "items": topics,
    }
    ctx["audit"].write("webhooks.topics", out)
    ctx["out"].emit(out)
    return 0


def _expected_signature(*, secret: str, payload: str) -> str:
    mac = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).digest()
    return base64.b64encode(mac).decode("utf-8")


def _normalize_signature(value: str | None) -> str:
    if not value:
        return ""
    return str(value).replace("X-Jobber-Hmac-SHA256=", "").strip()


def cmd_webhooks_verify_signature(args, ctx) -> int:
    body = str(getattr(args, "body", "") or "").strip()
    body_file = getattr(args, "body_file", None)
    if body_file:
        path = Path(body_file)
        if not path.exists():
            raise ValidationError(f"Body file not found: {path}")
        body = path.read_text(encoding="utf-8")
    if not body:
        raise ValidationError("Missing body via --body or --body-file")

    header_sig = _normalize_signature(str(getattr(args, "header", "") or ""))
    if not header_sig:
        raise ValidationError("Missing --header signature")

    secret = str(getattr(args, "secret", "") or ctx["cfg"].client_secret or "").strip()
    if not secret:
        raise ValidationError("Missing CLIENT_SECRET; set JOBBER_CLIENT_SECRET or use --secret")

    expected = _expected_signature(secret=secret, payload=body)
    valid = hmac.compare_digest(expected, header_sig)

    out = {
        "ok": True,
        "command": "webhooks.verify_signature",
        "matches": valid,
        "header_signature": header_sig,
        "computed_signature": expected,
        "signature_hint": expected[:8],
    }
    ctx["audit"].write("webhooks.verify_signature", out)
    ctx["out"].emit(out)
    return 0
