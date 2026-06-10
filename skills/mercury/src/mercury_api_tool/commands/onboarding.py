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
    if not _has_nonempty_env_value(lines, "MERCURY_API_BASE_URL"):
        missing.append("MERCURY_API_BASE_URL")
    if not _has_nonempty_env_value(lines, "MERCURY_API_TOKEN"):
        missing.append("MERCURY_API_TOKEN")
    # Optional, defaults to bearer.
    if not _has_nonempty_env_value(lines, "MERCURY_AUTH_SCHEME"):
        missing.append("MERCURY_AUTH_SCHEME (optional)")

    steps = [
        "Copy .env.example → .env (local-only; do not commit it).",
        "In your Mercury dashboard, create an API token (Settings → Developers/API → API tokens).",
        "If Mercury offers token permissions/scopes, choose read-only (least privilege).",
        "This tool is GET-only and cannot change anything inside Mercury.",
        "Open .env and fill the required values:",
        "  - MERCURY_API_BASE_URL=https://api.mercury.com/api/v1  (prod)",
        "    OR MERCURY_API_BASE_URL=https://api-sandbox.mercury.com/api/v1  (sandbox)",
        "  - MERCURY_API_TOKEN=secret-token:...  (keep private; do not paste into chat)",
        "  - MERCURY_AUTH_SCHEME=bearer  (or 'basic' if you prefer Basic auth)",
        "Run: mercury-api-tool --output json auth check",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": missing,
            "next_command": "mercury-api-tool --output json auth check",
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
        print("Next: mercury-api-tool --output json auth check")
    return 0
