from __future__ import annotations

from pathlib import Path


def _read_text_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    if not text:
        return []
    return text.splitlines(keepends=True)


def _looks_like_placeholder(value: str | None) -> bool:
    text = (value or "").strip().strip("'").strip('"')
    if not text:
        return True
    lowered = text.lower()
    if lowered in {
        "<todo>",
        "todo",
        "todo!",
        "replace_me",
        "replace-me",
        "replace with value",
        "your_value_here",
        "your_secret_here",
        "your_client_id",
        "your_client_secret",
        "your_token_here",
        "your_refresh_token",
    }:
        return True
    if lowered.startswith("<") and lowered.endswith(">"):
        return True
    return False


def _parse_env_entry(raw: str) -> tuple[str, str] | None:
    stripped = raw.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None
    candidate = stripped
    if candidate.startswith("export "):
        candidate = candidate[len("export ") :].lstrip()
    key, value = candidate.split("=", 1)
    return key.strip(), value.strip()


def _has_nonempty_env_value(lines: list[str], keys: set[str] | str) -> bool:
    keys_to_check = {keys} if isinstance(keys, str) else set(keys)
    for line in lines:
        parsed = _parse_env_entry(line)
        if not parsed:
            continue
        key, value = parsed
        if key in keys_to_check and not _looks_like_placeholder(value):
            return True
    return False


def _get_env_value(lines: list[str], key: str) -> str:
    for line in lines:
        parsed = _parse_env_entry(line)
        if not parsed:
            continue
        candidate, value = parsed
        if candidate == key and not _looks_like_placeholder(value):
            return value.strip("'").strip('"')
    return ""


def _required_auth_fields(auth_mode: str) -> list[str]:
    if auth_mode == "service_account_json":
        return ["GOOGLE_MERCHANT_API_SERVICE_ACCOUNT_JSON"]
    if auth_mode == "oauth_refresh_token":
        return [
            "GOOGLE_MERCHANT_API_OAUTH_REFRESH_TOKEN",
            "GOOGLE_MERCHANT_API_OAUTH_CLIENT_ID",
            "GOOGLE_MERCHANT_API_OAUTH_CLIENT_SECRET",
        ]
    if auth_mode == "adc":
        return []
    return []


def _missing_for_mode(lines: list[str], auth_mode: str) -> list[str]:
    if auth_mode == "service_account_json":
        if _has_nonempty_env_value(lines, {"GOOGLE_MERCHANT_API_SERVICE_ACCOUNT_JSON", "GOOGLE_MERCHANT_API_SERVICE_ACCOUNT_KEY_PATH"}):
            return []
        return ["GOOGLE_MERCHANT_API_SERVICE_ACCOUNT_JSON"]

    if auth_mode == "oauth_refresh_token":
        missing: list[str] = []
        if not _has_nonempty_env_value(
            lines,
            {
                "GOOGLE_MERCHANT_API_OAUTH_REFRESH_TOKEN",
                "GOOGLE_MERCHANT_API_OAUTH_REFRESH_TOKEN_FILE",
                "GOOGLE_MERCHANT_API_TOKEN_FILE",
            },
        ):
            missing.append("GOOGLE_MERCHANT_API_OAUTH_REFRESH_TOKEN")
        if not _has_nonempty_env_value(lines, {"GOOGLE_MERCHANT_API_OAUTH_CLIENT_ID", "GOOGLE_MERCHANT_API_CLIENT_ID"}):
            missing.append("GOOGLE_MERCHANT_API_OAUTH_CLIENT_ID")
        if not _has_nonempty_env_value(lines, {"GOOGLE_MERCHANT_API_OAUTH_CLIENT_SECRET", "GOOGLE_MERCHANT_API_CLIENT_SECRET"}):
            missing.append("GOOGLE_MERCHANT_API_OAUTH_CLIENT_SECRET")
        return missing

    return []


def _missing_fields(lines: list[str]) -> tuple[list[str], list[str], str]:
    missing: list[str] = []
    required: list[str] = []

    required.append("GOOGLE_MERCHANT_API_BASE_URL")
    if not _has_nonempty_env_value(lines, "GOOGLE_MERCHANT_API_BASE_URL"):
        missing.append("GOOGLE_MERCHANT_API_BASE_URL")

    required.append("GOOGLE_MERCHANT_API_AUTH_MODE")
    auth_mode = _get_env_value(lines, "GOOGLE_MERCHANT_API_AUTH_MODE").lower()
    if not auth_mode:
        missing.append("GOOGLE_MERCHANT_API_AUTH_MODE")
        return missing, required, auth_mode

    if auth_mode not in {"service_account_json", "oauth_refresh_token", "adc"}:
        missing.append("GOOGLE_MERCHANT_API_AUTH_MODE")
        return missing, required, auth_mode

    required.extend(_required_auth_fields(auth_mode))
    missing.extend(_missing_for_mode(lines, auth_mode))
    return missing, required, auth_mode


def cmd_onboarding(args: object, ctx: dict) -> int:
    out = ctx["out"]
    env_file = str(getattr(args, "env_file", ".env"))
    write_env = not bool(getattr(args, "no_write_env", False))

    env_path = Path(env_file)
    env_created = False

    if write_env and not env_path.exists():
        example_path = env_path.parent / ".env.example"
        if example_path.exists():
            env_path.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            env_path.write_text("", encoding="utf-8")
        env_created = True

    lines = _read_text_lines(env_path)
    missing, required_fields, auth_mode = _missing_fields(lines)

    steps = [
        "Copy .env.example → .env (local-only; do not commit it).",
        "Choose one auth mode in GOOGLE_MERCHANT_API_AUTH_MODE:",
        "  - service_account_json (recommended for own-account work)",
        "  - oauth_refresh_token (required for client-account work)",
        "  - adc (for Google-hosted systems)",
        "Set GOOGLE_MERCHANT_API_BASE_URL and fill mode fields:",
        "  - GOOGLE_MERCHANT_API_SERVICE_ACCOUNT_JSON for service-account mode",
        "  - GOOGLE_MERCHANT_API_OAUTH_REFRESH_TOKEN + GOOGLE_MERCHANT_API_OAUTH_CLIENT_ID + GOOGLE_MERCHANT_API_OAUTH_CLIENT_SECRET for OAuth mode",
        "Run: google-merchant-api-tool --output json auth check",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "auth_mode": auth_mode or None,
            "required_fields": required_fields,
            "missing": missing,
            "next_command": "google-merchant-api-tool --output json auth check",
            "steps": steps,
        },
    }

    if str(getattr(args, "output", "json")) == "json":
        out.emit(payload)
    else:
        print("To connect this tool to your API, do this once:")
        for i, s in enumerate(steps, start=1):
            print(f"{i}. {s}")
        if missing:
            print("")
            print(f"Missing in {env_file}: " + ", ".join(missing))
        print("")
        print("Next: google-merchant-api-tool --output json auth check")
    return 0
