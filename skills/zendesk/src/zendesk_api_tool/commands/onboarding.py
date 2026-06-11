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

    missing: list[str] = []
    if not _has_nonempty_env_value(lines, "ZENDESK_SUBDOMAIN") and not _has_nonempty_env_value(lines, "ZENDESK_BASE_URL"):
        missing.append("ZENDESK_SUBDOMAIN")
    if not _has_nonempty_env_value(lines, "ZENDESK_OAUTH_ACCESS_TOKEN"):
        # API token auth is recommended; treat those as missing unless OAuth token exists.
        if not _has_nonempty_env_value(lines, "ZENDESK_EMAIL"):
            missing.append("ZENDESK_EMAIL")
        if not _has_nonempty_env_value(lines, "ZENDESK_API_TOKEN"):
            missing.append("ZENDESK_API_TOKEN")

    steps = [
        "Copy .env.example → .env (local-only; do not commit it).",
        "Open .env and fill the required values:",
        "  - ZENDESK_SUBDOMAIN=acme  (if your URL is https://acme.zendesk.com)",
        "  - ZENDESK_EMAIL=you@company.com",
        "  - ZENDESK_API_TOKEN=...",
        "Optional (OAuth instead of API token):",
        "  - ZENDESK_OAUTH_ACCESS_TOKEN=...",
        "Run: zendesk-api-tool --output json auth check",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": missing,
            "next_command": "zendesk-api-tool --output json auth check",
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
        print("Next: zendesk-api-tool --output json auth check")
    return 0
