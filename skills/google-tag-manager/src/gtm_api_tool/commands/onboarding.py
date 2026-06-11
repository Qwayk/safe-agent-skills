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

    # Best-effort: infer auth mode from the file (no secrets printed).
    auth_mode = None
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        candidate = stripped
        if candidate.startswith("export "):
            candidate = candidate[len("export ") :].lstrip()
        k, v = candidate.split("=", 1)
        if k.strip() == "GTM_AUTH_MODE":
            auth_mode = v.strip().strip("'").strip('"') or None
            break

    missing: list[str] = []
    if auth_mode == "oauth_refresh_token":
        for k in ("GTM_OAUTH_CLIENT_ID", "GTM_OAUTH_CLIENT_SECRET", "GTM_OAUTH_REFRESH_TOKEN"):
            if not _has_nonempty_env_value(lines, k):
                missing.append(k)
    if auth_mode == "service_account_json":
        if not _has_nonempty_env_value(lines, "GTM_SERVICE_ACCOUNT_JSON_PATH"):
            missing.append("GTM_SERVICE_ACCOUNT_JSON_PATH")

    steps = [
        "Copy .env.example → .env (local-only; do not commit it).",
        "Open .env and choose an auth mode (ADC / OAuth refresh token / service account JSON).",
        "Fill the matching env keys (see docs/onboarding.md).",
        "Optional: set GTM_SCOPES (comma-separated) for least-privilege or custom scope sets.",
        "Run: gtm-api-tool --output json auth check",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": missing,
            "next_command": "gtm-api-tool --output json auth check",
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
        print("Next: gtm-api-tool --output json auth check")
    return 0
