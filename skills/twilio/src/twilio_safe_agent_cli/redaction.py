from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

REDACTED = "<REDACTED>"
_SECRET_KEYS = {
    "authorization",
    "auth_token",
    "token",
    "access_token",
    "refresh_token",
    "password",
    "secret",
    "api_key",
    "api_key_secret",
    "credential",
    "credentials",
    "sip_password",
}
_MANUAL_PII_KEYS = {
    "body",
    "message",
    "content",
    "from",
    "to",
    "phone_number",
    "phonenumber",
    "email",
    "emails",
    "identity",
    "username",
    "user_name",
    "displayname",
    "display_name",
    "givenname",
    "given_name",
    "familyname",
    "family_name",
    "address",
    "phonenumbers",
    "phone_numbers",
    "transcription",
    "transcript",
    "utterance",
    "text",
    "recording_url",
    "media_url",
    "mediaurl",
    "subject",
    "recipient",
    "participants",
}
_PHONE_RE = re.compile(r"(?<![A-Za-z0-9])(?:whatsapp:)?\+\d{7,15}(?!\d)", re.IGNORECASE)
_ENCODED_PHONE_RE = re.compile(r"%2B\d{7,15}(?!\d)", re.IGNORECASE)
_EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![\w.-])")
_SECRET_QUERY_RE = re.compile(
    r"([?&](?:access[_-]?token|refresh[_-]?token|token|api[_-]?key|key|secret|"
    r"x[_-]?amz[_-]?signature|signature|password|authorization|auth|credential)=[^&#\s]+)",
    re.IGNORECASE,
)


def _normalized_key(key: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(key).lower()).strip("_")


def _redact_string(value: str, secret_values: Iterable[str]) -> str:
    result = value
    for secret in sorted({item for item in secret_values if item}, key=len, reverse=True):
        result = result.replace(secret, REDACTED)
    result = _PHONE_RE.sub(REDACTED, result)
    result = _ENCODED_PHONE_RE.sub(REDACTED, result)
    result = _EMAIL_RE.sub(REDACTED, result)
    result = _SECRET_QUERY_RE.sub(lambda match: match.group(1).split("=", 1)[0] + "=" + REDACTED, result)
    return result


def redact(
    value: Any,
    *,
    pii_fields: set[str] | None = None,
    secret_values: Iterable[str] = (),
) -> Any:
    pii_keys = {_normalized_key(item) for item in (pii_fields or set())} | _MANUAL_PII_KEYS
    if isinstance(value, dict):
        output: dict[str, Any] = {}
        for key, item in value.items():
            normalized = _normalized_key(key)
            if (
                normalized in _SECRET_KEYS
                or normalized in pii_keys
                or normalized.endswith("_token")
                or normalized.endswith("_secret")
                or normalized.endswith("_password")
            ):
                output[str(key)] = REDACTED
            else:
                output[str(key)] = redact(
                    item,
                    pii_fields=pii_keys,
                    secret_values=secret_values,
                )
        return output
    if isinstance(value, list):
        return [redact(item, pii_fields=pii_keys, secret_values=secret_values) for item in value]
    if isinstance(value, tuple):
        return [redact(item, pii_fields=pii_keys, secret_values=secret_values) for item in value]
    if isinstance(value, str):
        stripped = value.strip()
        if (stripped.startswith("{") and stripped.endswith("}")) or (
            stripped.startswith("[") and stripped.endswith("]")
        ):
            try:
                decoded = json.loads(stripped)
            except json.JSONDecodeError:
                decoded = None
            if isinstance(decoded, (dict, list)):
                safe_decoded = redact(
                    decoded,
                    pii_fields=pii_keys,
                    secret_values=secret_values,
                )
                return json.dumps(safe_decoded, ensure_ascii=False, separators=(",", ":"))
        return _redact_string(value, secret_values)
    return value


def write_protected_json(path: str | Path, value: Any) -> str:
    destination = Path(path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    fd = os.open(destination, flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
    finally:
        try:
            os.chmod(destination, 0o600)
        except OSError:
            pass
    return str(destination)


def create_protected_json(path: str | Path, value: Any) -> str:
    """Create a new mode-600 JSON file without replacing an existing receipt."""

    destination = Path(path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(destination, flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
    finally:
        try:
            os.chmod(destination, 0o600)
        except OSError:
            pass
    return str(destination)


def file_receipt(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    raw = source.read_bytes()
    return {
        "path": str(source),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "protected_mode": oct(source.stat().st_mode & 0o777),
    }
