from __future__ import annotations

import re
from typing import Any


REDACTED = "[REDACTED]"

SECRET_WORDS = (
    "api_key",
    "apikey",
    "api-key",
    "authorization",
    "bearer",
    "client_secret",
    "client-secret",
    "cookie",
    "credential",
    "key",
    "password",
    "secret",
    "token",
    "webhook",
)

SECRET_KEY_PATTERN = r"(?:api[_-]?key|token|key|password|secret|client[_-]?secret|authorization|cookie|webhook|credential)"


def is_secret_name(name: str) -> bool:
    lowered = name.lower()
    return any(word in lowered for word in SECRET_WORDS)


def looks_secret_value(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    lowered = value.lower()
    return any(word in lowered for word in SECRET_WORDS)


def redact_value(value: Any, *, key_name: str = "") -> Any:
    if key_name and is_secret_name(key_name):
        return REDACTED
    if isinstance(value, dict):
        return {str(k): redact_value(v, key_name=str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_value(v, key_name=key_name) for v in value]
    if looks_secret_value(value):
        return REDACTED
    return value


def redact_pair_map(values: dict[str, str]) -> dict[str, str]:
    return {str(k): redact_value(v, key_name=str(k)) for k, v in values.items()}


def redact_text(text: str) -> str:
    safe = str(text)

    def redact_assignment(match: re.Match[str]) -> str:
        return f"{match.group(1)}{REDACTED}"

    def redact_quoted_assignment(match: re.Match[str]) -> str:
        return f"{match.group(1)}{REDACTED}{match.group(3)}"

    safe = re.sub(
        rf"((?:\"|')\s*{SECRET_KEY_PATTERN}\s*(?:\"|')\s*:\s*(?:\"|'))(.*?)(\"|')",
        redact_quoted_assignment,
        safe,
        flags=re.IGNORECASE,
    )
    safe = re.sub(
        rf"((?:\"|')\s*{SECRET_KEY_PATTERN}\s*(?:\"|')\s*:\s*)([^,\}}\]\s]+)",
        redact_assignment,
        safe,
        flags=re.IGNORECASE,
    )
    safe = re.sub(
        rf"(\b{SECRET_KEY_PATTERN}\b\s*:\s*)([^\s,;\}}\]]+)",
        redact_assignment,
        safe,
        flags=re.IGNORECASE,
    )
    safe = re.sub(
        rf"({SECRET_KEY_PATTERN}=)"
        r"[^&\s\"'<>]+",
        redact_assignment,
        safe,
        flags=re.IGNORECASE,
    )
    safe = re.sub(r"\S*(?:api[_-]?key|token|password|secret|client[_-]?secret|webhook)\S*", REDACTED, safe, flags=re.IGNORECASE)
    return safe


def _redact_pair_arg(raw: str) -> str:
    if "=" not in raw:
        return redact_text(raw)
    key, value = raw.split("=", 1)
    safe_value = redact_value(value, key_name=key)
    return f"{key}={safe_value}"


def redact_argv(argv: list[str]) -> list[str]:
    redacted: list[str] = []
    redact_next_as: str | None = None
    pair_flags = {"--path-param", "--query"}
    opaque_flags = {"--body-json": "[REDACTED_BODY_JSON]", "--body-file": "[REDACTED_BODY_FILE]"}

    for arg in argv:
        raw = str(arg)
        if redact_next_as == "pair":
            redacted.append(_redact_pair_arg(raw))
            redact_next_as = None
            continue
        if redact_next_as:
            redacted.append(redact_next_as)
            redact_next_as = None
            continue

        if raw in pair_flags:
            redacted.append(raw)
            redact_next_as = "pair"
            continue
        if raw in opaque_flags:
            redacted.append(raw)
            redact_next_as = opaque_flags[raw]
            continue

        matched_inline = False
        for flag, replacement in opaque_flags.items():
            if raw.startswith(f"{flag}="):
                redacted.append(f"{flag}={replacement}")
                matched_inline = True
                break
        if matched_inline:
            continue

        for flag in pair_flags:
            if raw.startswith(f"{flag}="):
                redacted.append(f"{flag}={_redact_pair_arg(raw.split('=', 1)[1])}")
                matched_inline = True
                break
        if matched_inline:
            continue

        redacted.append(redact_text(raw))

    return redacted


def redact_command(argv: list[str]) -> str:
    return "n8n-safe-agent-cli " + " ".join(redact_argv(argv))


def redact_url(url: str) -> str:
    out = redact_text(url)
    for marker in ("apiKey=", "api_key=", "api-key=", "token=", "key=", "password=", "secret="):
        if marker in out:
            prefix, rest = out.split(marker, 1)
            tail = rest.split("&", 1)
            out = prefix + marker + REDACTED + (("&" + tail[1]) if len(tail) > 1 else "")
    return out
