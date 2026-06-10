from __future__ import annotations


def redact_text(text: str, secrets: list[str] | tuple[str, ...]) -> str:
    out = str(text or "")
    for secret in secrets:
        token = str(secret or "").strip()
        if not token:
            continue
        out = out.replace(token, "[REDACTED]")
    return out
