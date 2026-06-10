from __future__ import annotations

from pathlib import Path


def _read_text_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    if not text:
        return []
    return text.splitlines(keepends=True)


def _has_nonempty_env_value(lines: list[str], key: str) -> bool:
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        candidate = stripped
        if candidate.startswith("export "):
            candidate = candidate[len("export ") :].lstrip()
        k, v = candidate.split("=", 1)
        if k.strip() == key and v.strip().strip("'").strip('"'):
            return True
    return False


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

    auth_mode = "adc"
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        candidate = stripped
        if candidate.startswith("export "):
            candidate = candidate[len("export ") :].lstrip()
        k, v = candidate.split("=", 1)
        if k.strip() == "GA4_AUTH_MODE":
            auth_mode = v.strip().strip("'").strip('"').strip() or "adc"
            break

    missing: list[str] = []
    if auth_mode == "service_account_json":
        if not _has_nonempty_env_value(lines, "GA4_SERVICE_ACCOUNT_JSON"):
            missing.append("GA4_SERVICE_ACCOUNT_JSON")
    if auth_mode == "oauth_refresh_token":
        for key in ("GA4_OAUTH_CLIENT_ID", "GA4_OAUTH_CLIENT_SECRET", "GA4_OAUTH_REFRESH_TOKEN"):
            if not _has_nonempty_env_value(lines, key):
                missing.append(key)

    steps = [
        "Copy .env.example → .env (local-only; do not commit it).",
        "Pick an auth mode (default is adc):",
        "  - GA4_AUTH_MODE=adc",
        "  - GA4_AUTH_MODE=service_account_json (requires GA4_SERVICE_ACCOUNT_JSON=/path/to/key.json)",
        "  - GA4_AUTH_MODE=oauth_refresh_token (requires GA4_OAUTH_CLIENT_ID/SECRET/REFRESH_TOKEN or .state/token.json)",
        "Optional overrides:",
        "  - GA4_SCOPES=https://www.googleapis.com/auth/analytics.readonly,...",
        "  - GA4_ADMIN_BASE_URL=https://analyticsadmin.googleapis.com/",
        "  - GA4_DATA_BASE_URL=https://analyticsdata.googleapis.com/",
        "Run: ga4-api-tool --output json auth check",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": missing,
            "next_command": "ga4-api-tool --output json auth check",
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
        print("Next: ga4-api-tool --output json auth check")
    return 0
