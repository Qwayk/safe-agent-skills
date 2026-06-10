from __future__ import annotations


def redact_secrets(text: str, secrets: list[str]) -> str:
    """
    Redact exact secret values from a string.

    This is intentionally simple: it's meant to prevent accidental echoing of env
    values in error messages (including mock exceptions in tests).
    """
    s = str(text or "")
    for secret in secrets:
        v = str(secret or "")
        if not v:
            continue
        s = s.replace(v, "<REDACTED>")
    return s

